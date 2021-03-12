#!/usr/bin/perl
use warnings;
use strict;
use autodie;
use HTTP::Tiny;
use JSON::Parse 'parse_json';
use Data::Dumper;
use File::Slurp;
use URI::Escape;
binmode STDOUT, ':encoding(UTF-8)';
use utf8::all;
use Text::Levenshtein::Damerau::XS qw/xs_edistance/;
use POSIX;
use Encode qw(decode encode);
use JSON;


#https://www.conservapedia.com/api.php?action=query&export&format=json&pageids=59436|96141|156027
my $baseurl = 'https://en.wikipedia.org/w/api.php?action=query&export&format=json&pageids=';

my @ids_to_download_1;
my @ids_to_download_2;

my %wikiredirectid_to_title;

open my $fh, "<:encoding(UTF-8)", "all_wiki_pages.tsv";
<$fh>;
#Conservapedia title	Conservapedia id	Exact_match	Conserva exact 2 Wiki redirect	Conserva redirects 2 Wiki exact
while (<$fh>) {
	my ($id, $is_redirect, $title) = split "\t";
	chomp $title;
	$wikiredirectid_to_title{$id} = $title;
}
close $fh;

open $fh, "<:encoding(UTF-8)", "conserva_wiki_matches.tsv";
<$fh>;

open my $logfh1, ">:encoding(UTF-8)", "conservaexact2wikiredirect/log_align.tsv";
print $logfh1 "Conservapedia page\tWikipedia redirect\tRedirect ID\n";

my %redirects_to_resolve;

open my $logfh2, ">:encoding(UTF-8)", "conservaredirect2wikiexact/log_align.tsv";
print $logfh2 "Conservapedia page\tSelected redirect\tAvailable conservapedia redirects that exist in Wikipedia\n";
while (<$fh>) {
	chomp;
	my ($conservaTitle, $consID, $wikiID, $conservaexact2wikiredir, $conservaredir2wikiexact) = split "\t";
	next unless $wikiID eq "NULL";
	if ($conservaexact2wikiredir =~ /^\d+$/) {
		#collect all redirects and resolve them in batch of 50s
		$redirects_to_resolve{$conservaTitle} = $conservaexact2wikiredir;
	}
	
	next if $conservaredir2wikiexact eq "NULL";
	my @ids = split /\|/, $conservaredir2wikiexact;
	my $min_distance = 1000;
	my $page_to_get = "";
	
	#here the mapping is many to many-> many redirects of conservapedia might match many pages on wikipedia
	#Example: Entry "Egyptian mythology" in Conservapedia does not exist in Wikipedia;
	#However, Eg. Myth. is the page where Imhotep, Osiris, Thoth, Hemen and Egyptian_religion
	#point to. All these pages exist in Wikipedia. To decide the best match, we use
	#a modified Levenshtein distance.
	
	for my $id (@ids) {
		my $wikititle = $wikiredirectid_to_title{$id};
		my $distance = xs_edistance($conservaTitle, $wikititle);
		if ($distance < $min_distance) {
			$min_distance = $distance;
			$page_to_get = $id;
		}
	}
	push @ids_to_download_2, $page_to_get;
	my @wikiredirects = map { $wikiredirectid_to_title{$_} } @ids;
	print $logfh2 "$conservaTitle\t$wikiredirectid_to_title{$page_to_get}\t".join "|", @wikiredirects."\n";
}
close $logfh2;
close $fh;


#find what the wikipedia page points to and save to file
my %redirects = %{resolve_redirects(\%redirects_to_resolve)};
my $redirects_as_json = encode_json \%redirects;
write_file("wikipedia_redirects_resolved.json",$redirects_as_json);

for my $wikiid (keys %redirects) {
	print $logfh1 "$redirects{$wikiid}->{from_title}\t$redirects{$wikiid}->{to_title}\t$redirects{$wikiid}->{to_id}\n";
	push @ids_to_download_1, $redirects{$wikiid}->{to_id};
} 
close $logfh1;

# 	my $title = $redirects_to_resolve{$id};
# 	my ($redirect_to_id, $wikiredirectedto_title) = @{resolve_redirect($wikiid)};
# 	push @ids_to_download_1, $redirect_to_id;		
# 	print $logfh1 "$conservaTitle\t$wikiredirectedto_title\n";
# 


batch_download_all_ids(\@ids_to_download_1, 50, "conservaexact2wikiredirect");
batch_download_all_ids(\@ids_to_download_2, 50, "conservaredirect2wikiexact");


sub batch_download_all_ids {
	my ($ids_to_down_ref, $batch_size, $folder) = @_;

	my @ids_to_download = @{$ids_to_down_ref};
	
	print "Downloading ".scalar(@ids_to_download)." files in folder '$folder'...\n";

	my $queries_needed = ceil(scalar(@ids_to_download)/$batch_size);
	print "Will perform $queries_needed queries\n";
	my $current_query = 0;
	
	
	my @ids_this_round = (1, 1);
	while (scalar(@ids_to_download)>0){
		@ids_this_round = splice @ids_to_download,0,$batch_size;
		my $ids = join "|", @ids_this_round;
		my $url = $baseurl."$ids";
		my $first_pageid = $ids_this_round[0];
		my $last_pageid = $ids_this_round[-1];	
		$current_query++;
		printf "(%03d/%d) ", $current_query, $queries_needed;
		
		next if -f "$folder/$first_pageid.xml"; #avoid redownloading stuff - note: if you changed 35, it might skip too many pages
		my $response = HTTP::Tiny->new->get($url);
		if ($response->{success}) {
			my $json = parse_json ($response->{content});
			my $content = $json->{query}->{export}->{"*"};
			open my $outfh, ">:encoding(UTF-8)", "$folder/$first_pageid.xml";
			print $outfh $content;
			close $outfh;
			print "Downloaded $first_pageid-$last_pageid\n";
			#select(undef, undef, undef, 0.1); #sleep 0.1 secs, not required for simple reads from mediawiki API
		} else {
			#sometimes the query fails. if it does, it progresses anyway, but we are leaving out (up to) 50 pages!
			#So, after finishing the download, go back and check all pages that are missing
			#and try to download them individually 
			print "Failed: $response->{status}\n" ;
			#exit;
		}
	
	}
	print "Completed download of folder $folder\n"
	
}


#take the list of redirects and return a hash with nicely complete data
sub resolve_redirects {
	my %redirects = %{ (shift) };
	my @redirects_to_resolve = values %redirects;
	my @redirects_in_batch = (1, 1);
	my %returnhash;
	print "Need to resolve ".scalar(@redirects_to_resolve)." redirect IDs...\n\n";
	my $queries_needed = ceil(scalar(@redirects_to_resolve)/50);
	print "Will perform $queries_needed queries\n";
	
	my $current_query = 0;
	while (scalar(@redirects_to_resolve)>0){	
		@redirects_in_batch = splice @redirects_to_resolve,0,50;
		my $ids = join "|", @redirects_in_batch;	
		$current_query++;
		printf "(%03d/%d) ", $current_query, $queries_needed;
		print "Querying ".scalar(@redirects_in_batch)." IDs using the Wikipedia API...";
		my $url = "https://en.wikipedia.org/w/api.php?action=query&prop=info&pageids=$ids&redirects=1&format=json&formatversion=2";
		my $response = HTTP::Tiny->new->get($url);
		if ($response->{success}) {
				print " Success.\n";
				my $json = parse_json (decode("UTF-8", $response->{content}));
				#UGH THE WIKIPEDIA API IS SICK WHILE IS IT SCRAMBLING THE ORDER
				my %former_titles;
				for my $titles (@{$json->{query}->{redirects}}) {
					$former_titles{$titles->{to}} = $titles->{from};
				}
				
				for my $page (@{$json->{query}->{pages}}) {
					if ($page->{missing}) {
						next;
					}
					my $title = $page->{title};
					my $from_title = $former_titles{$title};
					my $from_id = $redirects{$from_title};
					if (!defined $from_id) {
						print STDERR "Lost page '$title/$from_title' somehow\n";
						next;
					}
					my $id = $page->{pageid};
					$returnhash{$from_id} = {
						to_title => $title,
						from_title => $from_title,
						to_id => $id
					};
				}
		}
		else {
			print "\nCouldn't resolve redirect for wiki IDs. Server response: $response->{status}\nURL: $url\n" ;
		}
	}
	return \%returnhash;
}