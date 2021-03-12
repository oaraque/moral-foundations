#!/usr/bin/perl
use warnings;
use strict;
use File::Slurp;
binmode(STDOUT, ":utf8");

print "This reads everything in conservapedia_text or wiki_text and\n";
print "outputs it as separate text pages in txtpages, also producing\n";
print "a report of IDs and Titles in txtpages.tsv\n";
print "\nIt also check if all downloaded pages (save for redirects and disambiguation)\n";
print "were extracted as text\n";

my %redirects_and_ids;

my @folders = qw/conservaredirect2wikiexact exact_matches conservaexact2wikiredirect/;

for my $folder (@folders) {
	print "Processing folder $folder\n";
	die "You first need to run the previous script to create text folders" if !-d "$folder/text";
	
	
	my %downloaded_pages;

	my @files = glob("$folder/text/*");

	mkdir "$folder/txtpages" unless -d "$folder/txtpages";

	my %seen_pages;

	open my $reportfh, ">:encoding(UTF-8)", "$folder/txtpages.tsv";
	print $reportfh "PageID\tTitle\n";
	for my $file (@files) {
		open my $fh, "<:encoding(UTF-8)", $file;
		my $buffer = "";
		my $id = "";
		my $title = "";
		while (<$fh>) {
			if ($_ =~ /^<doc id="(\d+)" url=".*?" title="(.*)">/) {
				$id = $1;
				$title = $2;
				next;
			}
			if ($_ =~ /<\/doc>/) {
				if (!$seen_pages{$id}) {
					open my $pagefh, ">:encoding(UTF-8)", "$folder/txtpages/$id.txt";
					print $pagefh $buffer;
					close $pagefh;				
					print $reportfh "$id\t$title\n";
					delete $downloaded_pages{$id};
					$seen_pages{$id}=1;
				}
			
				$buffer = "";
				$id = "";
				$title = "";
				next;
			}
			$buffer = $buffer.$_;
		}
		close $fh;
	}

	for my $pageid (keys %downloaded_pages) {
		if ($downloaded_pages{$pageid}->{type} eq "N") {
			print "No text extracted 	for $pageid ($folder)\n";
		}
	}
	
}


