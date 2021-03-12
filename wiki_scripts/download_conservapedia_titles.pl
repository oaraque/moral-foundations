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

my $baseurl = 'https://www.conservapedia.com/api.php?action=query&list=allpages&format=json&continue=';
my $url = $baseurl;

if (-f "continue") {
	my $continue = read_file("continue");
	$url = $baseurl.$continue;
}

while (){
	my $response = HTTP::Tiny->new->get($url);
	if ($response->{success}) {
		my $json = parse_json ($response->{content});
		my $apcontinue = $json->{"continue"}->{"apcontinue"};
		
		#check for wide characters
		if ($apcontinue =~ /[^\x00-\xFF]/) {
			$response->{content} =~ /"apcontinue":"(.*)","continue":/;
			my $undecodedap = $1;
			$apcontinue = $undecodedap
		}		
		
		my $continue = $json->{"continue"}->{"continue"};
		my $continuestr = "$continue&apcontinue=$apcontinue";
		$url = $baseurl.$continuestr;
		my $first_pageid = $json->{"query"}->{"allpages"}->[0]->{"pageid"};
		write_file("$first_pageid.json",$response->{content});
		write_file("continue",$continuestr);
		print("Downloaded until $apcontinue (excluded)\n");
		select(undef, undef, undef, 0.125); #sleep 0.25 secs
	} else {
		print("Failed: $response->{status} $response->{reasons}");
		exit;
	}
}