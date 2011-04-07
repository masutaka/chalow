#!/usr/bin/env perl
# $Id: clsearch.cgi,v 1.12 2003/08/29 15:22:44 yto Exp $
# clsearch.cgi - chalow により HTML 化された ChangeLog を検索する CGI
use strict;

### User Setting from here
# お好みにあわせて変えて下さい
my $home_page_url = "http://nais.to/~yto/";
my $home_page_name = "たつをのホームページ";
my $numnum = 20; # 一度に表示できる数
my $css_file = "diary.css";
### to here

use Jcode;
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
	open(F, "< $fn") or die "Can't open $fn : $!\n";
	my $all = join('', <F>);
	$all = Jcode->new($all)->euc;
	close(F);

	my $date = "";
	while ($all =~ m%(<div\sclass=("day">.+?</h2>|"section">.+?<!--eos-->))%gsmx) {
	    my $item = $1;
	    if ($2 =~ /^"day"/) {
		$date = $item;
		next;
	    }

	    my $tmpi = $item;
	    $tmpi =~ s/[\n\t]+//g; # 改行消し
	    $tmpi =~ s/<.+?>//g; # タグ抜き

	    if ($tmpi =~ m/$key/i) {
		$cnt++;
		next if ($cnt < $from + 1 or $cnt >= $from + 1 + $numnum);
		my $ostr = "[$cnt] $date\n";
		# タグ中の文字列はハイライトしない
		my @tmp = split(/(<.+?>)/, $item);
		foreach my $ii (@tmp) {
		    $ii =~ s|($key)|<strong style="background-color:yellow">$1</strong>|gix if ($ii !~ /^</);
		    $ostr .= $ii;
		}
		$outstr .= $ostr."</div>\n"; # <div class="day"> の閉じ
	    }
	}
    }
}

my $page_max = int(($cnt - 1) / $numnum);

my ($qkey) = ($q->query_string =~ /(key=[^&]+)/);

# ■■■ 過去記事表示のための選択棒 ■■■
my $bar = "";
my ($navip, $navin);
if ($page_max != 0) { # 1ページのみのときは選択棒なし
    for (my $i = 0; $i <= $page_max; $i++) {
	if ($from / $numnum == $i) {
	    $bar .= "<strong>".($i + 1).'</strong>';
	} else {
	    $bar .= $q->a({-href => "$myself?from=".($i * $numnum)."&".$qkey},
			  $i + 1);
	}
	$bar .= " ";

	if ($from / $numnum == $i - 1) {
	    $navin = $q->a({-href => "$myself?from=".($i * $numnum).
				"&".$qkey}, "[ 次へ ]");
	} elsif ($from / $numnum == $i + 1) {
	    $navip = $q->a({-href => "$myself?from=".($i * $numnum).
				"&".$qkey}, "[ 前へ ]");
	}

    }
#    $bar .= "(${numnum}件ずつ表示)";
}

if ($cnt == 0) {
    print "<p>見つかりませんでした。</p>\n";
} else {
    print "<p>$cnt 件 見つかりました。</p>\n";
}

print qq(<p>$navip $bar $navin</p><div class="body">$outstr</div><p>$navip $bar $navin</p>
<a href="index.html">ChangeLog INDEX</a>
 / <a href="$home_page_url">$home_page_name</a>
<div style="text-align:right">Powered by 
<a href="http://nais.to/~yto/tools/chalow/"><strong>chalow</strong></a></div>);

print $q->end_html(), "\n";

exit;
