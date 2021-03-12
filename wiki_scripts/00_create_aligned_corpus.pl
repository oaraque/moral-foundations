#!/usr/bin/perl
use warnings;
use strict;
use File::Copy;
use Data::Dumper;
use File::Slurp;
use JSON;
# This script fetches all downloaded pages from wikipedia and conservapedia
# that should be stored in the two subfolders, and aligns them "side by side"
# by assigning them a new ID.
# For example, Conservapedia page 101807 and Wikipedia page 236906, both about
# Paolo Veronese, will be assigned a new id (e.g. 7216) and can be found as
# 7216.conserva and 7216.wiki respectively. A mapping file between the new and original IDs
# is also created.
# The process is repeated for exact matches, and the two types of redirects; all these 
# conditions are kept in separate folders. IDs are not overlapping across folders (e.g.
# 7216 is an exact match, and there will be no 7216.wiki or 7216.conserva in other folders)

mkdir 'aligned' if ! -d 'aligned';
mkdir 'aligned/exact' if ! -d 'aligned/exact';
mkdir 'aligned/redirects' if ! -d 'aligned/redirects';

my %downloaded_conservapedia_pages;
open my $fh, "<:encoding(UTF-8)", "wikipedia/conserva_wiki_matches.tsv";
<$fh>;
while (<$fh>) {
	chomp;
	my ($conserva_title, $conserva_id, $exact_match, $conservaexact2wikiredirect, $conservaredirect2wikiexact) = split "\t";
	my $hashref = {
		conserva_title => $conserva_title,
		conserva_id => $conserva_id,
		exact_match => $exact_match,
		conservaexact2wikiredirect => $conservaexact2wikiredirect,
		conservaredirect2wikiexact => $conservaredirect2wikiexact	
	};
	$downloaded_conservapedia_pages{$conserva_id}=$hashref;
}
close $fh;

my %conservapedia_ids;
open $fh, "<:encoding(UTF-8)", "conservapedia/conservapedia_page_ids_all.tsv";
<$fh>;
while (<$fh>) {
	chomp;
	my ($id, $title) = split "\t";
	$conservapedia_ids{$id}=$title;
}
close $fh;




my $new_id = 1;
open my $exactoutfh, ">:encoding(UTF-8)", "aligned/exact.tsv";
print $exactoutfh "New_ID\tConservapedia_title\tConservapedia_ID\tWikipedia_title\tWikipedia_ID\n";

#open my $disambiguatefh, ">:encoding(UTF-8)", "aligned/disambiguate_this.tsv";
#print $disambiguatefh "Conserva_title\tWikipedia_redirects_to\tWiki_target_id\tConservapedia_redirects_matching_wiki\tWiki_IDs\n";

open my $redirectfh, ">:encoding(UTF-8)", "aligned/redirectlog.tsv";
print $redirectfh "New_ID\tMatched conserva title\tOriginal conserva title\tMatched wiki title\tOriginal wiki title\n";

my %wikipedia_redirects = %{decode_json(read_file("wikipedia/wikipedia_redirects_resolved.json"))};

my $not_found = 0;
for my $conserva_id (keys %downloaded_conservapedia_pages) {
	my %page = %{$downloaded_conservapedia_pages{$conserva_id}};
	if ($page{exact_match} ne "NULL") {
		my $wiki_id = $page{exact_match};
		my $wiki_title = $page{conserva_title}; #it's an exact title match, so it's the same
		my $wiki_file = "./wikipedia/exact_matches/txtpages/$wiki_id.txt";
		my $conserva_file = "./conservapedia/txtpages/$conserva_id.txt";		
		if (!-e $wiki_file) {
			$not_found++;
			warn "Couldn't find exact file $wiki_file for this item: ".Dumper(\%page);
			next;	
		}
		if (!-e $conserva_file) {
			$not_found++;
			warn "Couldn't find exact file $wiki_file for this item: ".Dumper(\%page);
			next;	
		}		
		print $exactoutfh "$new_id\t$page{conserva_title}\t$page{conserva_id}\t$wiki_title\t$wiki_id\n";
		copy $wiki_file, "aligned/exact/$new_id.wiki" unless -e  "aligned/exact/$new_id.wiki";
		copy $conserva_file, "aligned/exact/$new_id.conserva" unless -e  "aligned/exact/$new_id.conserva";
		$new_id++;
		next;
	}
	
# 	if we have both, save to a log and skip; the ideal solution is to manually check WHAT the redirects are
# 	and delete the duplicated or non-optimal ids, (if they are not too many)
# 	if ($page{conservaexact2wikiredirect} ne "NULL" && $page{conservaredirect2wikiexact} ne "NULL") {
# 		1conservapedia->1wiki redirect
# 		my $wiki_id_matching = $page{conservaexact2wikiredirect};
# 		my $wikipedia_redirects_to_title = $wikipedia_redirects{$wiki_id_matching}->{to_title};
# 		my $target_wiki_id = $wikipedia_redirects{$wiki_id_matching}->{to_id};
# 		
# 		my $lineout = "$page{conserva_title}\t$wikipedia_redirects_to_title\t$target_wiki_id\t";
# 		print $disambiguatefh "$page{conserva_title}\t$wikipedia_redirects_to_title\t$target_wiki_id\t";
# 		
# 		many conservapedia -> 1 wiki full page
# 		my @conserva_redirects = split /\|/, $page{conservaredirect2wikiexact};
# 		for my $redirect_id (@conserva_redirects) {
# 			$lineout = $lineout."$conservapedia_ids{$redirect_id}||";
# 			print $disambiguatefh "$conservapedia_ids{$redirect_id}||";
# 		}
# 		print $disambiguatefh "\n";
# 	}
	if ($page{conservaexact2wikiredirect} ne "NULL") {# && $page{conservaredirect2wikiexact} eq "NULL") {
		#ONE conservapedia entry matches ONE wikipedia redirect
		my $wiki_id_matching = $page{conservaexact2wikiredirect};
		my $wikipedia_redirects_to_title = $wikipedia_redirects{$wiki_id_matching}->{to_title};
		#find the ID of the page that was actually downloaded
		my $target_wiki_id = $wikipedia_redirects{$wiki_id_matching}->{to_id};
		
		my $wiki_file = "./wikipedia/conservaexact2wikiredirect/txtpages/$target_wiki_id.txt";
		my $conserva_file = "./conservapedia/txtpages/$conserva_id.txt";
		if (!-e $wiki_file) {
			$not_found++;
			warn "Couldn't find redirect file $wiki_file for this item: ".Dumper(\%page);
			next;	
		}
		if (!-e $conserva_file) {
			$not_found++;
			warn "Couldn't find redirect file $conserva_file for this item: ".Dumper(\%page);
			next;	
		}
			
		print $redirectfh "$new_id\t\t$page{conserva_title}\t$wikipedia_redirects{$wiki_id_matching}->{from_title}\t$wikipedia_redirects{$wiki_id_matching}->{to_title}\n";
		copy $wiki_file, "aligned/redirects/$new_id.wiki" unless -e  "aligned/redirects/$new_id.wiki";
		copy $conserva_file, "aligned/redirects/$new_id.conserva" unless -e  "aligned/redirects/$new_id.conserva";
		$new_id++;
		next;
	}
	elsif ($page{conservaredirect2wikiexact}) {
		#1. find all redirects (remember to split on /\|/ not just "|")
		#2. find the id and name of the pages they point at
		#4. find the name that is closest to whatever using levensthein, use theo ther script to make it consistent
		#5. that is the id that has been downloaded
		
	}	
}

print STDERR "Didn't find $not_found files\n";