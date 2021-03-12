#!/usr/bin/perl
use warnings;
use strict;
use autodie;
use File::Slurp;

print "This will join the individual pages in the wiki folders
into a single xml dump, to be processed with wikiextractor\n";

my @folders = qw/exact_matches conservaexact2wikiredirect conservaredirect2wikiexact/;

for my $folder (@folders) {
	my @files = glob("$folder/*.xml");
	open my $outfh, ">:encoding(UTF-8)", "$folder/whole_dump_xml.xml";
	print $outfh '<mediawiki>\n';

	for my $filename (@files) {
		my @content = read_file($filename, { binmode => 'encoding(UTF-8)'});

		#remove first and last line (open/close mediawiki tags)
		shift @content;
		pop @content;
	
		print $outfh join "", @content;
	}
	print $outfh '\n</mediawiki>';
}