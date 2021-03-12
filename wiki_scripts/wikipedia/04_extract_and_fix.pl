#!/usr/bin/perl
use warnings;
use strict;
use autodie;
use File::Copy;

print "Using wikiextractor to process whole_dump_xml. This will take a while...\n";

my @folders = qw/conservaredirect2wikiexact exact_matches conservaexact2wikiredirect/;

for my $folder (@folders) {
	print "Processing folder $folder\n";
	mkdir "$folder/text" if !-d "$folder/text";
	
	system("wikiextractor", "--no-templates", "-o", "$folder/text", "$folder/whole_dump_xml.xml");

	print "Extraction completed, fixing filenames\n";
	my @subfolders = glob("$folder/text/*");

	my $start = 0;
	for my $subfolder (@subfolders) {
		next unless -d $folder;
		my @files = glob("$subfolder/*");
		for my $path (@files) {
			my $filename = $path;
			$filename =~ s/^.*\///;
			$filename =~ s/(wiki|text)_/text_$start/;
			move $path, "$folder/text/$filename";
		}
		rmdir $subfolder;
		$start++;
	}
}