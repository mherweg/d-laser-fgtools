#!/usr/bin/perl

########
#       Sets pylon orientation for pylon chains in newobjects table
#
#       Jon Stockill 2006/06/16
########

use DBI;
use Math::Trig qw(great_circle_direction deg2rad rad2deg);
use Data::Dumper;

$db=(DBI->connect('DBI:Pg:dbname=landcover;host=hostname','username','password'));

$way=$ARGV[0]||-1;

if ($way==-1)
{
  print "\nYou must specify the id of the way to be updated.\n\n";
  exit 0;
};

print "Way=".$way."\n";

$query="select *,y(AsText(wkb_geometry)) as ob_lat,x(AsText(wkb_geometry)) as ob_lon from fgs_objects where ob_text like 'Pylon (W-".$way."%' order by ob_text;";
$dblist=$db->prepare($query);
$dblist->execute();

$count=0;

while ($pylon=$dblist->fetchrow_hashref)
{
  $pylonlist->[$count]->{"id"}=$pylon->{'ob_id'};
  $pylonlist->[$count]->{"lat"}=$pylon->{'ob_lat'};
  $pylonlist->[$count]->{"lon"}=$pylon->{'ob_lon'};
  $pylonlist->[$count]->{"txt"}=$pylon->{'ob_text'};
  $pylonlist->[$count]->{"hdg"}=$pylon->{'ob_heading'};
  $count++;
};

#
#	Set heading for first pylon
#

$heading = rad2deg(great_circle_direction(deg2rad($pylonlist->[0]->{"lon"}), 
                                          deg2rad(90-$pylonlist->[0]->{"lat"}),
                                          deg2rad($pylonlist->[1]->{"lon"}), 
                                          deg2rad(90-$pylonlist->[1]->{"lat"})));
$heading=sprintf("%3.2f",$heading);
$heading+=90;
$heading-=360 if $heading>360;
$difference="Start";
$query="update fgs_objects set ob_heading=".$heading." where ob_id=".$pylonlist->[0]->{"id"}.";";
print $query."\n";  
$update=$db->prepare($query);
$update->execute();

#
#	Set heading for non-end pylons
#

foreach ($loop=1;$loop<=$count-1;$loop++)
{
  $in = rad2deg(great_circle_direction(deg2rad($pylonlist->[$loop-1]->{"lon"}), 
                                        deg2rad(90-$pylonlist->[$loop-1]->{"lat"}),
                                        deg2rad($pylonlist->[$loop]->{"lon"}), 
                                        deg2rad(90-$pylonlist->[$loop]->{"lat"})));
  $out = rad2deg(great_circle_direction(deg2rad($pylonlist->[$loop]->{"lon"}), 
                                        deg2rad(90-$pylonlist->[$loop]->{"lat"}),
                                        deg2rad($pylonlist->[$loop+1]->{"lon"}), 
                                        deg2rad(90-$pylonlist->[$loop+1]->{"lat"})));

  $heading=sprintf("%3.2f",($in+$out)/2);
  $heading+=90;
  $heading-=360 if $heading>360;
  $difference=sprintf("%d",abs($in-$out));
  $query="update fgs_objects set ob_heading=".$heading." where ob_id=".$pylonlist->[$loop]->{"id"}.";";
  print $query."\n";  
  $update=$db->prepare($query);
  $update->execute();
};

#
#	Set heading for last pylon
#

$heading = rad2deg(great_circle_direction(deg2rad($pylonlist->[$count-2]->{"lon"}), 
                                          deg2rad(90-$pylonlist->[$count-2]->{"lat"}),
                                          deg2rad($pylonlist->[$count-1]->{"lon"}), 
                                          deg2rad(90-$pylonlist->[$count-1]->{"lat"})));
$heading=sprintf("%3.2f",$heading);
$heading+=90;
$heading-=360 if $heading>360;
$difference="End";
$query="update fgs_objects set ob_heading=".$heading." where ob_id=".$pylonlist->[$count-1]->{"id"}.";";
print $query."\n";  
$update=$db->prepare($query);
$update->execute();

exit 0;
