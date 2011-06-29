#!/usr/bin/env perl
# $Id: add-extent.pl,v 1.3 2003/08/25 11:50:33 yto Exp $
# HTML の img タグに width と height を足す

use strict;
use File::Copy;

# identify 自動設定
my $IDENTIFY = `which identify`;
die "NO identify!" unless ($IDENTIFY =~ /identify$/);
chomp $IDENTIFY;

if (@ARGV == 0) {
    print << "USAGE";
usage: prog <file> [file]...
USAGE
    ;
} else {

    for my $fname (@ARGV) {

	# HTML ファイルを一気に読み込む
	open(IN, $fname) or die;
	my $all = join('', <IN>);
	close(IN);

	# cache ファイル
	my $cfn = $fname;
	$cfn =~ s!/[^/]*$!!;	# パス
	$cfn .= "/cache_extent-info";
	my %file_info;
	my $file_info_update_flag = 0;
	if (open(F, $cfn)) {
	    while(<F>) {
		next if (/^\#/ or /^\s*$/);
		my @c = split(/\s/);
		if (@c == 3) {
		    $file_info{$c[0]} = [@c[1..2]];
		}
	    }
	    close(F);
	}

	# img タグの部分を取りだす。
	my @con = split(/(<img.+?>)/ims, $all);

	next if (scalar(@con) == 1); # img タグが無いファイルは何もしない

	my $num = 0;
	for (my $i = 0; $i < @con; $i++) {

	    if ($con[$i] =~ /^(<img.+?>)/ims) {
		my $in = $1;

		# width と height の両方が設定されている場合は何もしない
		next if ($in =~ /\W((width|height)\W.+?\W){2}/i); # ad hoc

		# width or height を消す
		$con[$i] =~ s/\s+(width|height)=[^\s]+//gims;

		# 画像ファイル名を取り出す
		die unless ($in =~ /\ssrc="?(\S+?)"?[\s>]/i);
		my $imgfn = $1;

		# identify で width と height を取得
		next unless (-e $imgfn);
		my ($w, $h);
		if (defined $file_info{$imgfn}) {
		    ($w, $h) = @{$file_info{$imgfn}};
		} else {
		    ($w, $h) = (`$IDENTIFY $imgfn` =~ /(\d+)x(\d+)/);
		    $file_info{$imgfn} = [$w, $h];
		    $file_info_update_flag = 1;
#		    print join("----", @{$file_info{$imgfn}}),"\n";
		}
		die if $?;

		# img タグ内に width と height を追加
		$con[$i] =~ s|>$| width="$w" height="$h">|ims;
		$num++;
	    }

	    # cache ファイルの書き込み
	    if ($file_info_update_flag and open(F, "> $cfn")) {
		foreach my $f (sort keys %file_info) {
		    print F "$f @{$file_info{$f}}\n";
		}
		close(F);
	    }
	}

	next if ($num == 0);	# 変更箇所なし

	# 変更箇所があったら、元のファイルを退避してから、上書きする
	copy($fname, "$fname.bak") or die;
	open(OUT, "> $fname") or die;
	print OUT join("", @con);
	close(OUT);
    }

}
