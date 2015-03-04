#!/usr/bin/env perl

use strict;
use warnings;

use MediaWiki::API;
use Gtk3 '-init';

sub print_key_values {
  my $ref = shift;

  my @keys = keys %{$ref};

  foreach (@keys) {
    print "key: $_ value: $ref->{$_}\n";
  }
}

sub get_page {
  my $title = shift || "gnome";
  my $mw = MediaWiki::API->new;
  $mw->{config}->{api_url} = 'http://en.wiktionary.org/w/api.php';

  my $content = $mw->api( {
      action => 'query',
      prop => 'revisions',
      rvprop => 'content',
      titles => $title } )
  || die $mw->{error}->{code} . ': ' . $mw->{error}->{details};

  print "----------------\n";
  print_key_values $content;
  print "----------------\n";
  print_key_values $content->{query};
  print "----------------\n";
  print_key_values $content->{query}->{pages};
  print "----------------\n";

  my ($pageid, $pageref) = each %{$content->{query}->{pages}};
  print "$pageid: $pageref\n";

  print_key_values $pageref;
  print "----------------\n";
  my @revs = @{$pageref->{revisions}};
  foreach (@revs) {
    print "elem: $_\n";
  }
  print_key_values $revs[0];
  print "----------------\n";

  return $revs[0]->{'*'};
}

sub insert_definition {
  my $definition = shift @_;
  our $buffer;

  my $iter = $buffer->get_end_iter;
  $buffer->insert($iter, $definition . "\n");
}

sub parse_content {
  my $orig = shift;
  my @lines = split '\n', $orig;

  my @parsed = ();

  foreach (@lines) {
    if ($_ =~ /(Etymology )/) {
      push @parsed, $_;
    }
    if ($_ =~ /^# /) {
      push @parsed, $_;
      insert_definition $_;
    }
  }

  return join "\n", @parsed;
}

sub on_entry_activate {
  our $entry;
  our $buffer;

  my ($start, $end) = $buffer->get_bounds;
  $buffer->delete($start, $end);

  my $iter = $buffer->get_start_iter;
  $buffer->insert_with_tags_by_name(
    $iter,
    $entry->get_text . "\n",
    "query-title");

  my $content = get_page($entry->get_text);
  $content = parse_content($content);
}

sub main {
  my $win = Gtk3::Window->new('toplevel');
  my $vbox = Gtk3::VBox->new;
  our $entry = Gtk3::Entry->new;
  my $scroll = Gtk3::ScrolledWindow->new;
  our $buffer = Gtk3::TextBuffer->new;
  $buffer->create_tag("query-title", "left-margin", "10", "weight", "1000", "scale", "1.6");
  my $text_view = Gtk3::TextView->new_with_buffer($buffer);
  $vbox->pack_start($entry, 0, 0, 6);
  $vbox->pack_start($scroll, 1, 1, 6);
  $scroll->add($text_view);
  $win->add($vbox);

  $win->set_title('GNOME Wiktionary');
  $win->set_default_size(600, 600);
  $text_view->set_wrap_mode('word');

  $entry->signal_connect(activate => \&on_entry_activate);
  $win->signal_connect(delete_event => sub { Gtk3::main_quit });

  $win->show_all;
  Gtk3::main;
}

main @ARGV;
