package ChangeLogReader;
use strict;
#use vars qw(@ISA @EXPORT $VERSION $OLD_CODE);
#require Exporter;
#@ISA = qw(Exporter);
#@EXPORT = qw(store_changelog store_entry store_entry2 debug_print);
#$VERSION = '0.1';

sub new {
    my $class = shift;
    my $self = {};
    my %param = @_;
    for (keys %param) { $self->{lc($_)} = $param{$_} } 
    return bless $self, $class;
}

sub debug_print {
    my ($self) = @_;    
    foreach my $ymd (reverse sort keys %{$self->{all}}) {
	my $ent = $self->{all}->{$ymd};
	print "=" x 60, "\n";
	print "ENTRY ID: $ymd\n";
	print "message-top:",$ent->{'message-top'},"\n"
	    if (defined $ent->{'message-top'});
	print "message-bottom:",$ent->{'message-bottom'},"\n"
	    if (defined $ent->{'message-bottom'});
	for (my $i = $ent->{curid}; $i >= 1; $i--) {
	    print "-" x 60, "\n";
	    print "ITEM ID: $ymd-$i\n";
	    print "ITEM HEADER:>>>>",$ent->{$i}->{ho},"<<<<\n";
	    print "ITEM CATEGORY:",join(",",@{$ent->{$i}->{cat}}),"\n"
		if (defined $ent->{$i}->{cat});
	    print "ITEM AUTHOR:>>>>",$ent->{$i}->{a},"<<<<\n";
	    print "ITEM CONTENT:>>>>",$ent->{$i}->{co},"<<<<\n";
	}
    }
}


sub store_changelog_file {
    my ($self, $fname) = @_;

    open(F, $fname) || die "file open error $fname : $!";
    binmode(F);
    my @entlines;
    while (<F>) {
	if (/^(\d{4}-\d\d-\d\d)/) {
	    $self->store_entry(\@entlines) if (@entlines > 0);
	    @entlines = ();
	} elsif (/^\t?__DATA__.*$/) {
	    last;
	}
	push @entlines, $_;    
    }
    $self->store_entry(\@entlines) if (@entlines > 0);
    close F;
}


sub store_entry {
    my ($self, $linesp) = @_;

    # Processing entry header
    my $eh = shift @$linesp;

    return unless ($eh =~ /^\d{4}-\d\d-\d\d/);

    my ($ymd, $y, $m, $d, $user) 
        = ($eh =~ /^((\d\d\d\d)-(\d\d)-(\d\d))(?:.*?\s\s)(.+)?/);

    $self->{all}->{$ymd}->{eh} = $ymd;
    my $entp = $self->{all}->{$ymd};

    $user =~ s/</&lt;/g;
    $user =~ s/>/&gt;/g;
#    print "($ymd, $y, $m, $d, $user) \n";
#    print "<<<<<$eh>>>>>>>\n";

    # Processing each item
    my @ilines;
    my @items;
    foreach (@$linesp) {
	if (s/^( {8}| {0,7}\t|)\* //) {
	    push @items, [@ilines] if (@ilines > 0 and $ilines[0] !~ /^\s*$/);
	    @ilines = ();
	}
	push @ilines, $_;
    }
    push @items, [@ilines] if (@ilines > 0 and $ilines[0] !~ /^\s*$/);

    foreach (reverse @items) {
	$self->store_item($entp, $_, $ymd, $user);
    }

    if ($entp->{curid} == 0) {
	# If the entry doesn't have any item, delete it.
	# It will be happend when all items in the entry are private items.
	# Notice: pragma items are ignored.
	delete $self->{all}->{$ymd};
	return;
    }

    my $ent = $self->{all}->{$ymd};
    for (my $i = $ent->{curid}; $i >= 1; $i--) {
	if (defined $ent->{$i}->{cat}) {
	    map {$self->{CAT}->{$_}++} @{$ent->{$i}->{cat}};
	}
    }

    $self->{STAT}->{ym}{$y."-".$m}++; # for month_page_list
    $self->{STAT}->{md}{$m."-".$d}{$y} = 1; # for SameDateJump
    # {"ym"} : 各年月に含まれている日付エントリ数
    # {"md"} : 同じ月日を持つ年 for same date jump

    if ($self->{stop_date} != 0) {
	my $cdate = $y * 10000 + $m * 100 + $d;
	if ($self->{stop_date} > $cdate) {
	    delete $self->{all}->{$ymd};
	}
    }
}


# 文字コードを euc にしておく???????
sub store_item {
    my ($self, $entp, $linesp, $ymd, $user) = @_;
#    $entp = $self->{all}->{$ymd};

    my $ih = shift @$linesp;
    # item header - case 1: "* AAA: \n"
    # item header - case 2: "* AAA:\n"
    # item header - case 3: "* AAA: BBB\n"
    # item header - case 4: "* AAA\n"
    my ($rest) = ($ih =~ s/:(\s.*)$/:/s) ? $1 : ""; # for case 1,2,3
    $rest =~ s/^ +//;
    my $cont = $rest.join("", @$linesp);
    if ($ih =~ /^p:/) { # Ignoring private items
	return;
    } elsif ($ih =~ /^(message-top|message-bottom):/) {	# pragma items
	$entp->{$1} = $rest.$cont;
	return;
    }

    # item ID : Y in XXXX-XX-XX-Y
    $entp->{curid}++;

    # Processing item header
    # # If 1st line doesn't have ": ", it will become item header.
    my @cat;
#    $ih =~ s/(:|\s+)$//g;
    $ih =~ s/(:|\s*)$//sg;	# Triming trailing spaces and ":"
#    print "[[[[$ih]]]\n";
    if ($ih =~ s/\s*\[(.+)\]$//) { # category
	@cat = split(/\s*\]\s*\[\s*/, $1);
    }

    # Processing item content
    $cont =~ s/^( {8}| {0,7}\t)//gsm; 
    $cont =~ s/\s+$/\n/g;		# Triming trailing spaces and CR
    $cont =~ s/\r//g;

    # Storing item information in hash
    $entp->{$entp->{curid}}{ho} = $ih;
    $entp->{$entp->{curid}}{co} = $cont;
    $entp->{$entp->{curid}}{a} = $user if (defined $user);
    @{$entp->{$entp->{curid}}{cat}} = @cat if (@cat > 0);

#    print "<<<<<$ih>>>>>>>\n";
}

1;
