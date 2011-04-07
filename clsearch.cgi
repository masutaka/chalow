#!/usr/bin/env perl
# $Id: clsearch.cgi,v 1.5 2003/06/12 11:58:20 yto Exp $
# clsearch.cgi - HTML 化された ChangeLog (by chalow) を検索するCGI
use strict;

### User Setting from here
# お好みにあわせて変えて下さい
my $home_page_url = "http://nais.to/~yto/";
my $home_page_name = "たつをのホームページ";
my $numnum = 20; # 一度に表示できる数
my $css_file;
### to here

# nkf 自動設定 --- 日本語コードで悩まされないために...
my $NKF = `which nkf`;
chomp $NKF;
die "NO NKF!" if ($NKF !~ /nkf$/); 

use CGI;
my $q = new CGI;

my $myself = $q->url();		# このCGIのURL
my $key = $q->param('key');
my $from = $q->param('from') || 0;

# ■■■ HTML head 出力 ■■■
print "Content-type: text/html; charset=euc-jp\n\n";
print qq(<html><head><title>CHALOW Search</title>
<meta http-equiv="Content-Type" content="text/html; charset=EUC-JP">);
print qq(<link rel=stylesheet href="$css_file" media=all>\n)
    if defined $css_file;
print qq(</head><body><a href="index.html">ChangeLog INDEX</a>
 / <a href="$home_page_url">$home_page_name</a>\n);
print $q->startform, $q->textfield('key'), $q->submit, $q->endform, "\n";

# ■■■ 検索 ■■■
my $outstr = "";
my $cnt = 0;

if (defined $key) {
    my @fl = reverse sort <[0-9][0-9][0-9][0-9]-[0-9][0-9].html>;
    for my $fn (@fl) {
	open(F, "$NKF -ed $fn |") or die "file open error: $fn\n";
	my $date = "";
	$/ = "";
	while (<F>) {
	    chomp;
	    s/^.+?<pre>\n//sm;	# for first day on the month
	    next unless (/^<a\sname/ or /^[\s\t]+\*/);
	    if (/^<.+?>(\d\d\d\d-\d\d-\d\d)</) {
		$date = $_;
		next;
	    } elsif (! /^[\s\t]+\*/) {
		next;
	    }

	    my $item = $_;

	    my $line = $date." ".$item;
	    $line =~ s/[\n\t]+//g; # 改行消し
	    $line =~ s/<.+?>//g; # タグ抜き
	    
	    # $line でパターンマッチし、マッチしたら $item を出力する。
	    if ($line =~ m/$key/i) {
		$cnt++;

		my $ostr = "[$cnt] $date\n\n";

		# タグ中の文字列はハイライトしない
		my @tmp = split(/(<.+?>)/, $item);
		foreach my $ii (@tmp) {
		    $ii =~ s|($key)|<font
			style="background-color: pink">$1</font>|gix
			    if ($ii !~ /^</);
		    $ostr .= $ii;
		}
		$ostr .= "\n\n";
		
		if ($cnt >= $from + 1 and
		    $cnt < $from + 1 + $numnum) {
		    $outstr .= $ostr;
		}
	    }
	}
	close F;
    }
}

my $page_max = int(($cnt - 1) / $numnum);

my ($qkey) = ($q->query_string =~ /(key=[^&]+)/);

# ■■■ 過去記事表示のための選択棒 ■■■
my $bar = "";
if ($page_max != 0) { # 1ページのみのときは選択棒なし
    $bar = "<hr>\n";
    for (my $i = 0; $i <= $page_max; $i++) {
	if ($from / $numnum == $i) {
	    $bar .= $i + 1;
	} else {
	    $bar .= $q->a({-href => "$myself?from=".($i * $numnum)."&".$qkey},
			  $i + 1);
	}
	$bar .= " ";
    }
    $bar .= "(${numnum}件ずつ表示)";
}

if ($cnt == 0) {
    print "見つかりませんでした。\n";
} else {
    print "$cnt 件 見つかりました。\n";
}

print qq($bar<hr><pre>$outstr</pre>$bar<hr>
<a href="index.html">ChangeLog INDEX</a>
 / <a href="$home_page_url">$home_page_name</a>
<div align="right">Powered by 
<a href="http://nais.to/~yto/tools/chalow/"><b>chalow</b></a></div>);

print $q->end_html(), "\n";

exit;
