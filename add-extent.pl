#!/usr/bin/env perl
# $Id: add-extent.pl,v 1.1 2003/06/09 13:47:07 yto Exp $
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
		die unless (-e $imgfn);
		my ($w, $h) = (`$IDENTIFY $imgfn` =~ /(\d+)x(\d+)/);
		die if $?;

		# img タグ内に width と height を追加
		$con[$i] =~ s|>$| width="$w" height="$h">|ims;
		$num++;
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
