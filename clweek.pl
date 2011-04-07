#!/usr/bin/env perl
# $Id: clweek.pl,v 1.1 2003/01/18 01:53:09 yto Exp $
# usage: prog ChangeLogFileName > NewFileName
# before: 2000-06-12  YAM Tat  <yto@example.com>
# before: Mon Jun 12 08:05:49 2000  YAM Tat  <yto@example.com>
# after:  2000-06-12 (Mon)  YAM Tat  <yto@example.com>

use POSIX;
use Time::Local;
setlocale( LC_TIME, "C" );

my %mon;
for ( $i = 0; $i < 12; $i++ ) {
    $mon{
        (   'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
            )[$i]
        }
        = $i + 1;
}

while (<>) {

    # for  2000-06-12  YAM Tat  <yto@example.com>
    s/^(\d{4})-(\d\d)-(\d\d)\s\s/
        sprintf "%04d-%02d-%02d (%s)  ", $1, $2, $3,
	get_weekday_name($1, $2, $3)/ex;

    # for  Mon Jun 12 08:05:49 2000  YAM Tat  <yto@example.com>
    s/^([A-Z]..)\s([A-Z]..)\s+(\d+).+(\d{4})/
        sprintf "%04d-%02d-%02d (%s)", $4, $mon{$2}, $3, 
	get_weekday_name($4, $mon{$2}, $3)/ex;

    print;
}

sub get_weekday_name {
    ( $y, $m, $d ) = @_;
    return strftime "%a", localtime timelocal( 0, 0, 0, $d, $m - 1, $y );
}
