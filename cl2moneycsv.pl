#!/usr/bin/env perl
# $Id: cl2moneycsv.pl,v 1.1 2003/07/31 14:36:20 yto Exp $
# ChangeLog メモで家計簿!
#  ref. <http://nais.to/~yto/doc/zb/0016.html#kakeibo>
#
# ■フォーマット
# * .+?買物ログ:
# ^\t[費目][スペース][コメント][金額]$
# - スペースは半角でも全角でも良い。
# - 金額は半角数字。桁カンマは入れてはいけない。
#
# ■注意
# - 日本語コードは EUC を仮定
# - Excel に読み込ませる前に文字コードを Shift-JIS に変換する必要あり
#
# ■記述例＆実行例
# 
# $ cat ChangeLog
# 2003-08-02  YAMASHITA Tatsuo  <yto@example.com>
# 
# 	* できごと: だらだらしてた。
# 
# 	* p:買物ログ: 
# 	食 スーパー 1050
# 	本 コンビニで雑誌 380
# 
# 2003-08-01  YAMASHITA Tatsuo  <yto@example.com>
# 
# 	* できごと: 川崎で映画。
# 
# 	* p:買物ログ: 
# 	外 ファーストフード 525
# 	遊 映画 2000
# 	交 川崎往復 420
# 	食 スーパー 780
# 
# 2003-07-31  YAMASHITA Tatsuo  <yto@example.com>
# 
# 	* できごと: 渋谷に出掛けた。
# 
# 	* p:買物ログ: 
# 	外 レストラン 3000
# 	交 渋谷往復 640
# 	雑 ペンとメモ帳 550
# 
# $ cl2moneycsv.pl ChangeLog
#           ,  外,  食,  交,  遊,  本,  音,  雑,  衣,  他
# 2003.07.31,3000,   0, 640,   0,   0,   0, 550,   0,   0
# 2003.08.01, 525, 780, 420,2000,   0,   0,   0,   0,   0
# 2003.08.02,   0,1050,   0,   0, 380,   0,   0,   0,   0
# $ cl2moneycsv.pl -m ChangeLog  (←月毎に集計)
#           ,  外,  食,  交,  遊,  本,  音,  雑,  衣,  他
# 2003-07,3000,   0, 640,   0,   0,   0, 550,   0,   0
# 2003-08, 525,1830, 420,2000, 380,   0,   0,   0,   0
# $ cl2moneycsv.pl -m ChangeLog | nkf -s > kaimono.csv

use strict;

### コマンドライン引数
use Getopt::Long;
Getopt::Long::Configure('bundling');
my ($mon_mode);
GetOptions('m|monthly' => \$mon_mode);

# 費目 an item of expendidure
my @lioe = ('外', '食', '交', '遊', '本', '音', '雑', '衣', '他');

my $date;	
my $inside_flag = 0;

my %entry = ();
while (<>) {
    if (/^((\d{4}-\d\d)-\d\d)/) { # 日付をキープ
	if (defined $mon_mode) {
	    $date = $2;		# = year-month
	} else {
	    $date = $1;		# = year-month-day
	    $date =~ s|-|.|g;	# for Excel
	}
	next;
    } elsif (/買物ログ:/) {	# 家計簿データ記述ブロックの始まり
	$inside_flag = 1;
    } elsif ($inside_flag == 1) { # ブロック内
	if (/^\s*$/ and $inside_flag == 1) { # ブロックの終わり
	    $inside_flag = 0;
	} elsif (/^\t(.+?)(\s|\xa1\xa1).*(\s|\xa1\xa1)(\d+)$/) {
	    $entry{$date}->{$1} += $4;
	}
    }
}


print " " x 10, ",  ", join(',  ', @lioe), "\n";

foreach my $date (sort keys %entry) {
    print "$date,";
    print join(',', map {sprintf "%4d", $entry{$date}{$_}} @lioe), "\n";
}
