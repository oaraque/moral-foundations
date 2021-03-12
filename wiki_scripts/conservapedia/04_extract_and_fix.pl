#!/usr/bin/perl
use warnings;
use strict;
use autodie;
use File::Copy;

print "Using wikiextractor to process whole_dump_xml. This will take a while...\n";
#system("wikiextractor", "--no-templates", "whole_dump_xml.xml");

die "Wikiextractor didn't create a 'text' folder" unless -d 'text';
print "Extraction completed, fixing filenames\n";

my @folders = glob('text/*');

my $start = 0;
for my $folder (@folders) {
	next unless -d $folder;
	my @files = glob("$folder/*");
	for my $file (@files) {
		my $filename = $file;
		$filename =~ s/^.*\///;
		$filename =~ s/(wiki|text)_/text_$start/;
		move $file, "text/$filename";
	}
	rmdir $folder;
	$start++;
}

move "text", "conservapedia_text";

