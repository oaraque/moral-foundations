#!/usr/bin/perl
use warnings;
use strict;
use autodie;
use Encode qw(decode encode);
use JSON;
use File::Slurp;
use HTTP::Tiny;
use POSIX;
use JSON::Parse 'parse_json';
use Data::Dumper;
use URI::Escape;
binmode STDOUT, ':encoding(UTF-8)';
use utf8::all;
use Text::Levenshtein::Damerau::XS qw/xs_edistance/;
use Encode qw(decode encode);

my %redirects_to_resolve;

open my $fh, "<:encoding(UTF-8)", "all_wiki_pages.tsv";
<$fh>;
#Conservapedia title	Conservapedia id	Exact_match	Conserva exact 2 Wiki redirect	Conserva redirects 2 Wiki exact
while (<$fh>) {
	chomp;
	my ($id, $is_redirect, $title) = split "\t";
	next unless $is_redirect eq "1";
	$title =~ s/_/ /g;
	$redirects_to_resolve{$title} = $id;
}
close $fh;

my $json = encode_json(resolve_redirects(\%redirects_to_resolve));
write_file("test.json",$json);
print "All done\n";

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