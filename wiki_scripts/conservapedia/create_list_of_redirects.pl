#!/usr/bin/perl
use warnings;
use strict;
binmode(STDOUT, ":utf8");


my %id_from_title;
my %downloaded_pages;
my %pages_pointing_here;
open my $fh, "<:encoding(UTF-8)", "conservapedia_downloaded_pages.tsv";
while (<$fh>) {
	chomp;
	my ($type, $id, $title, $redirect) = split "\t";
	$downloaded_pages{$id} = {
		type => $type,
		title => $title,
		redirect => $redirect
	};
	$id_from_title{$title} = $id;
	$pages_pointing_here{$id} = [];
}
close $fh;


for my $id (keys %downloaded_pages) {
	if ($downloaded_pages{$id}->{type} eq "R") {
		my $redirect_title = $downloaded_pages{$id}->{redirect};
		my $target_id = $id_from_title{$redirect_title};
		next unless $target_id; #skip pages that were not downloaded, usually crap
		push @{$pages_pointing_here{$target_id}}, $id;
	}
}


print "PageID\tPage Title\tIDs that send here\tTitles that send here\n";
for my $id (keys %downloaded_pages) {
	next unless $downloaded_pages{$id}->{type} eq "N";
	my $title = $downloaded_pages{$id}->{title};
	my @ids = @{$pages_pointing_here{$id}};
	my @titles;
	for my $refid (@ids) {
		push @titles, $downloaded_pages{$refid}->{title};
	}
	print "$id\t$title\t".(join "|", @ids)."\t".(join "|", @titles)."\n";
}