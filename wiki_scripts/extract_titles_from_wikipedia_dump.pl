#!/usr/bin/perl
use warnings;
use strict;
use autodie;
use Term::ProgressBar;

my $progress = Term::ProgressBar->new ({name => "Read lines", count => 6185, ETA   => 'linear'});
$progress->minor(0);

open my $infh, "<", "enwiki-20210101-page.sql";
my $curline = 0;
print "PageID\tIs_Redirect\tPage_Title\n";
while (my $line = <$infh>) {
	$curline++;
	chomp $line;
	next unless $line =~ /^INSERT INTO/;
	$progress->update($curline);	
	my @matches = $line =~ /\(\d+,.*?NULL\)/g;
	for my $match (@matches) {
		$match =~ s/^\((\d+),(\d+),'//;
		my $pageid = $1;
		my $namespace = $2;
		$match =~ s/','.*?',(0|1),(0|1),[0-9.]+,('\d+'),('\d+'|NULL),\d+,\d+,'wikitext',NULL\)$//;
		my $is_redirect = $1;
		my $title = $match;
		next unless $namespace == 0;
		next if $title =~ /(disambiguation)/;
		print "$pageid\t$is_redirect\t$title\n";
	}
}
close $infh;