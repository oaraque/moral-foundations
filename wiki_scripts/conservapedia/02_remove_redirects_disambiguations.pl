#!/usr/bin/perl
use warnings;
use strict;
use autodie;

print "This removes from the downloaded pages:\n";
print "1. Disambiguation pages\n";
print "2. Redirects, keeping the page they point to, unless it's a disambiguation page\n";
print "3. The main page (1.xml)\n";

my @pages_to_remove;
open my $fh, "<:encoding(UTF-8)", "conservapedia_downloaded_pages.tsv";
while (<$fh>) {
	my ($page_type, $page_id, @other) = split "\t";
	push @pages_to_remove, "xml_individual_pages/$page_id.xml" if $page_type =~ /^(R|D)$/;
}

push @pages_to_remove, "xml_individual_pages/1.xml";

#delete in one go, BAM!
unlink @pages_to_remove;


print("Deleted ".scalar(@pages_to_remove)." pages\n");