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


#download pages from conservapedia by using the query API


#https://www.conservapedia.com/api.php?action=query&export&format=json&pageids=59436|96141|156027
my $baseurl = 'https://www.conservapedia.com/api.php?action=query&export&format=json&pageids=';

my @ids_to_download;


#it tries to download everything contained in this file:
open my $fh, "<", "conservapedia_page_ids_all.tsv";
<$fh>;
while (<$fh>) {
	my ($id, $title) = split "\t";
	next if -f "xml_individual_pages/$id.xml";
	push @ids_to_download, $id;
}
close $fh;


my @ids_this_round = (1, 1);
my $pages_per_batch = 50; #change how many pages are downloaded per query (max 50)
while (scalar(@ids_to_download)>0){
	
	@ids_this_round = splice @ids_to_download,0,$pages_per_batch;
	my $ids = join "|", @ids_this_round;
	my $url = $baseurl."$ids";
	my $first_pageid = $ids_this_round[0];
	my $last_pageid = $ids_this_round[-1];	
	next if -f "xmls/$first_pageid.xml"; #avoid redownloading stuff - note: if you changed 35, it might skip too many pages
	my $response = HTTP::Tiny->new->get($url);
	if ($response->{success}) {
		my $json = parse_json ($response->{content});
		my $content = $json->{query}->{export}->{"*"};
		open my $outfh, ">:encoding(UTF-8)", "xmls/$first_pageid.xml";
		print $outfh $content;
		close $outfh;
		print "Downloaded $first_pageid-$last_pageid\n";
		#select(undef, undef, undef, 0.1); #sleep 0.1 secs, not required for simple reads from mediawiki API
	} else {
		#sometimes the query fails. if it does, it progresses anyway, but we are leaving out (up to) 50 pages!
		#So, after finishing the download, go back and check all pages that are missing
		#and try to download them individually 
		print "Failed: $response->{status}\n";
		#exit;
	}
	
}
print "Completed download\n";