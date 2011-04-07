#!/usr/bin/perl
# $Id: clsearch.cgi,v 1.1 2007-10-19 22:08:03+09 tatsuoyamashita Exp tatsuoyamashita $
# clsearch.cgi - chalow により HTML 化された ChangeLog を検索する CGI
use strict;

### User Setting from here
# お好みにあわせて変えて下さい

my $numnum = 10;		# 一度に表示できる数
my $css_file = "diary.css";

# for simple mode
my $simple_template = << "_TEMPLATE"
<div class="section">%%CNT%%. %%DATE%%  %%CONT%%</div>
_TEMPLATE
    ;

# for item mode
my $item_template = << "_TEMPLATE"
%%CONT%%
_TEMPLATE
    ;

# for list mode
my $list_template = << "_TEMPLATE"
%%DATE%%  %%CONT%%<br/>
_TEMPLATE
    ;

# simple mode でマッチした文字列をはさむタグ
my ($open_tag, $close_tag) = 
    (qq(<em style="background-color:yellow">), "</em>");

### to here

use CGI;
my $q = new CGI;

my $myself = $q->url();		# このCGIのURL
my $key = $q->param('key');
my $from = $q->param('from') || 0;
my $clen = $q->param('context_length') || 200;
my $mode = $q->param('mode');	# 0:simple mode, 1:item mode, 2:list mode

if (defined $q->param('date')) {
    $mode = 2;
    $key = "date:".$q->param('date');
}

if ($mode == 2) {		# リストモードのときは全部一気に出す
    $numnum = 100000000;
    $from = 0;
}

if (defined $q->param('cat')) {
    $mode = 1;
    $key = "cat:".$q->param('cat');
    $key =~ s/^(.+)$/"$1"/ if ($key =~ / /);
}


# ■■■ HTML head 出力 ■■■
print "Content-type: text/html; charset=euc-jp\n\n";


# ■■■ 検索 ■■■
my $outstr = "";
my $cnt = 0;


sub clean {
    local ($_) = @_;
#    s/^"(.+)"$/$1/;
    s/(.)/'\x'.unpack("H2", $1)/gie;
    return $_;
}

if (defined $key and $key !~ /^\s*$/) {
    $key =~ s/\xa1\xa1/ /g;	# ad hoc
    $key =~ s/\s+$//;
    $key =~ s/^\s+//;

    my @keys = ($key =~ /(".+?"|\S+)/g);
#    @keys = map {s/^"(.+)"$/$1/; s/(.)/'\x'.unpack("H2", $1)/gie; $_;} @keys;
    @keys = map {s/^"(.+)"$/$1/; $_;} @keys;

    my $fn = "cl.itemlist";
    open(F, "< $fn") or die "Can't open $fn : $!\n";
    binmode(F);
    while (<F>) {
	my ($date, $c) = (/^(.+?)\t(.+)$/);
	my @regular_keys;

	my $match_num = 0;
	foreach my $k (@keys) {	# 毎回やるのは無駄。あとで直すべし。
	    if ($k =~ /^date:(.+)$/) {
		my $tmp = clean($1);
		$match_num++ if ($date =~ /\[$tmp/);
	    } elsif ($k =~ /^cat:(.+)$/) {
		my $tmp = clean($1);
		$match_num++ if ($c =~ /^.+\[$tmp\].*\t.*$/);
 	    } else {
		my $tmp = clean($k);
		$match_num++ if ($c =~ m|$tmp|i);
		push @regular_keys, $tmp;
	    }
	}
	my $pkey = $regular_keys[0] if (@regular_keys > 0); # 代表キー

#print @keys,"<br>\n";
	
	if ($match_num == @keys) {
#	if ($c =~ m|$pkey|i) {
	    $cnt++;
	    #next if ($cnt < $from + 1);last if ($cnt >= $from + 1 + $numnum);
	    next if ($cnt < $from + 1 or $cnt >= $from + 1 + $numnum);
	    # ↑高速化の余地

	    my $tmp_tmpl = $simple_template;
	    if ($mode == 0) { # シンプルモード
		if (defined $pkey and 
		    $c =~ m|^.*?(.{0,$clen})($pkey)(.{0,$clen}).*?$|i) {
		    my ($pre, $k, $pos) = ($1, $2, $3);
		    # 80-ff が奇数だったら 1 バイト削除 (要ブラッシュ up)
		    $pre =~ s!^[\x80-\xff](([\x80-\xff]{2})*[\x00-\x7f])!$1!;
		    $pre =~ s!^[\x80-\xff](([\x80-\xff]{2})*)$!$1!;
		    $pos =~ s!^(.*?[\x00-\x7f]([\x80-\xff]{2})*?)[\x80-\xff]$!$1!;
		    $pos =~ s!^(([\x80-\xff]{2})*?)[\x80-\xff]$!$1!;
		    $c = qq($pre$k$pos);
		    my $p = join('|', @regular_keys);
		    $c =~ s!($p)!$open_tag$1$close_tag!gi;
		}
	    } elsif ($mode == 1) { # アイテムモード
		my ($file, $id) = ($date =~ /href="(.*?.html).*?">\[(.+?)\]/);
		$c = get_item($file, $id);
		$tmp_tmpl = $item_template;
	    } elsif ($mode == 2) { # リストモード
		$c =~ s/\t.*$//;
		$tmp_tmpl = $list_template;
	    }
	    
	    $tmp_tmpl =~ s/%%CNT%%/$cnt/g;
	    $tmp_tmpl =~ s/%%DATE%%/$date/g;
	    $tmp_tmpl =~ s/%%CONT%%/$c/g;
	    $outstr .= $tmp_tmpl;
	}
    }
    close(F);
}



# ■■■ 過去記事表示のための選択棒 ■■■
my $page_max = int(($cnt - 1) / $numnum);
my ($qkey) = ($q->query_string =~ /(key=[^&]+)/);
($qkey) = ($q->query_string =~ /(cat=[^&]+)/) if ($qkey eq "");

my $bar = "";
my ($navip, $navin);
if ($page_max != 0) {		# 1ページのみのときは選択棒なし
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
}

if ($cnt == 0) {
    print "<p>見つかりませんでした。</p>\n";
} else {
    print "<p>$cnt 件 見つかりました。</p>\n";
}


my $page_template = << "__TEMPLE"

<html><head><title>CHALOW Search</title>
<meta http-equiv="Content-Type" content="text/html; charset=EUC-JP">
<link rel=stylesheet href="$css_file" media=all>
</head><body><a href="index.html">ChangeLog INDEX</a>

<form method="get" action="clsearch.cgi" 
    enctype="application/x-www-form-urlencoded">
<input type="text" name="key" value="@{[$q->escapeHTML($key)]}" />
<input type="checkbox" name="mode" value="1" @{[($mode)? "checked":""]}/>
<!--
<input type="radio" name="mode" value="0" @{[($mode==0)? "checked":""]}/>
<input type="radio" name="mode" value="1" @{[($mode==1)? "checked":""]}/>
<input type="radio" name="mode" value="2" @{[($mode==2)? "checked":""]}/>
-->
<input type="submit">
</form>

<p>$navip $bar $navin</p>
<div class="body">$outstr</div>
<p>$navip $bar $navin</p>
<a href="./">ChangeLog INDEX</a>
<div style="text-align:right">Powered by 
<a href="http://chalow.org/"><strong>chalow</strong></a></div>
</body></html>
__TEMPLE

    ;

#print $q->Dump();
print $page_template;

exit;


### ファイルから、IDにより指定されたitemを取りだす
my %file_cache;
sub get_item {
    my ($file, $id) = @_;
    my $all;
    if (not defined $file_cache{$file}) {
	open(F2, $file) or die "can't open $file : $!";
	$file_cache{$file} = join('', <F2>);
	close F2;
    }
    my $start = "<!-- start:$id -->";
    my $end = "<!-- end:$id -->";
    my ($item) = ($file_cache{$file} =~ /($start.+$end)/sm);
    return $item;
}
