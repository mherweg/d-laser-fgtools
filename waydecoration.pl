#!/usr/bin/perl

use POSIX;
use LWP::Simple;
use Math::Trig qw(great_circle_distance great_circle_destination great_circle_bearing deg2rad rad2deg);
use Getopt::Long;
use File::Slurp;

sub getnode
{
  my ($nodeid)=@_;
  my $nodexml=get("http://api.openstreetmap.org/api/0.6/node/$nodeid");
  my ($lat,$lon)=$nodexml=~/lat=\"([0-9\-\.]+)\" lon=\"([0-9\-\.]+)\"/gis;
  return ($nodeid,$lat,$lon);
};

sub rad2m
{
  my ($rad)=@_;
  return $rad*6377997;
};

sub m2rad
{
  my ($m)=@_;
  return $m/6377997;
};

sub bucket_span {
  my ($lat) = (@_);
  if ($lat>= 89.0 ) {
    return 360.0;
  } elsif ($lat>= 88.0 ) {
    return 8.0;
  } elsif ($lat>= 86.0 ) {
    return 4.0;
  } elsif ($lat>= 83.0 ) {
    return 2.0;
  } elsif ($lat>= 76.0 ) {
    return 1.0;
  } elsif ($lat>= 62.0 ) {
    return 0.5;
  } elsif ($lat>= 22.0 ) {
    return 0.25;
  } elsif ($lat>= -22.0 ) {
    return 0.125;
  } elsif ($lat>= -62.0 ) {
    return 0.25;
  } elsif ($lat>= -76.0 ) {
    return 0.5;
  } elsif ($lat>= -83.0 ) {
    return 1.0;
  } elsif ($lat>= -86.0 ) {
    return 2.0;
  } elsif ($lat>= -88.0 ) {
    return 4.0;
  } elsif ($lat>= -89.0 ) {
    return 8.0;
  } else {
    return 360.0;
  }
}

sub tile_index {

  my $EPSILON = 0.0000001;
  my ($lon, $lat) = (@_);
  my $lon_floor = POSIX::floor($lon);
  my $lat_floor = POSIX::floor($lat);
  my $span = bucket_span($lat);

  my $x;
  if ($span < $EPSILON) {
    $lon = 0;
    $x = 0;
  } elsif ($span <= 1.0) {
    $x = int(($lon - $lon_floor) / $span);
  } else {
    if ($lon >= 0) {
      $lon = int(int($lon/$span) * $span);
    } else {
      $lon = int(int(($lon+1)/$span) * $span - $span);
      if ($lon < -180) {
        $lon = -180;
      }
    }
    $x = 0;
  }

  my $y;
  $y = int(($lat - $lat_floor) * 8);

  my $index = 0;
  $index += ($lon_floor + 180) << 14;
  $index += ($lat_floor + 90) << 6;
  $index += $y << 3;
  $index += $x;

  return $index;
}

my @way;

# Constants
my $pi=3.14159265358979323846;

#Defaults
my $spacing=25;
my $wayid=3688451;
my $nodecount=0;
my $carryoffset=0;
my $format="sql";
my $submitter="Waydecorator";
my $country="gb";
my $desc="Street furniture";
my %output;
$output->{'centre'}=0;
$output->{'left'}=0;
$output->{'right'}=0;
my %leftpt;
$leftpt->{'offset'}=5;
my %rightpt;
$rightpt->{'offset'}=5;

$result = GetOptions ("s|spacing=f" => \$spacing,
                      "lo|left-offset=f"    => \$leftpt->{'offset'},
                      "ro|right-offset=f"   => \$rightpt->{'offset'},
                      "l|left"    => \$output->{'left'},
                      "r|right"   => \$output->{'right'},
                      "c|centre"  => \$output->{'centre'}, 
                      "w|way=i"   => \$wayid,
                      "f|format=s" => \$format,
                      "d|desc=s" => \$desc,
                      "m|model=s" => \$model,
                      "country=s" => \$country,
                      "submitter=s" => \$submitter);

my $wayxml=get("http://api.openstreetmap.org/api/0.6/way/$wayid");

# Assemble way data structure
foreach ($wayxml=~/nd ref=\"([0-9]+)\"/gis)
{
  ($nodeid,$lat,$lon)=&getnode($_);
  $way[$nodecount]->{'node'}=$nodeid;
  $way[$nodecount]->{'lat'}=$lat;
  $way[$nodecount]->{'lon'}=$lon;
  $nodecount++;
};

# Process data structure
$max=@way-1;
open(FILE,">waydecoration.gpx") if $format eq "gpx";
open(FILE,">waydecoration.stg") if $format eq "stg";
print FILE "<?xml version=\"1.0\"?>
<gpx version=\"1.1\">\n" if $format eq "gpx";
for ($node=0 ; $node<$max ; $node++)
{

  $distancerad = great_circle_distance(deg2rad($way[$node]->{'lon'}),deg2rad(90-$way[$node]->{'lat'})
                                    ,deg2rad($way[$node+1]->{'lon'}),deg2rad(90-$way[$node+1]->{'lat'}));
  $bearingrad = great_circle_bearing(deg2rad($way[$node]->{'lon'}),deg2rad(90-$way[$node]->{'lat'})
                                    ,deg2rad($way[$node+1]->{'lon'}),deg2rad(90-$way[$node+1]->{'lat'}));
  $distancem=&rad2m($distancerad);
  $refpointtotal=int(($distancem-$carryoffset)/$spacing);
  if ($refpointtotal==0)
  {
    $carryoffset-=$distancem;
  }
  else
  {
    for ($refptindex=1 ; $refptindex<=$refpointtotal ; $refptindex++)
    {
      $refpt->{'offset'}=$carryoffset+($refptindex*$spacing);
      ($refpt->{'lon'},$refpt->{'lat'},$refpt->{'direction'}) = great_circle_destination(deg2rad($way[$node]->{'lon'}), deg2rad(90-$way[$node]->{'lat'}), $bearingrad, &m2rad($refpt->{'offset'}));
      $reflatdeg=rad2deg($refpt->{'lat'});
      $reflondeg=rad2deg($refpt->{'lon'});
      $heading=rad2deg($bearingrad);
      $tile=tile_index($reflondeg,$reflatdeg);
      $heading=rad2deg($bearingrad);
      if ($output->{'centre'}==1)
      {
        print FILE "  <wpt lat='".$reflatdeg."' lon='".$reflondeg."'><name>C $heading</name></wpt>\n" if $format eq "gpx";
        print FILE "OBJECT_SHARED ".$model." ".$reflondeg." ".$reflatdeg." 0 0\n" if $format eq "stg";
        print "insert into fgs_objects values (DEFAULT,DEFAULT,DEFAULT,'$desc (W-$wayid C)',GeometryFromText('POINT($reflondeg $reflatdeg)',4326),-9999,0,null,$heading,'$country',$model,1,$tile,$wayid,'$submitter',true,DEFAULT);\n" if $format eq "sql";
      };
      $offsetbrg=$bearingrad+($pi/2);
      if ($output->{'left'}==1)
      {
        ($leftpt->{'lon'},$leftpt->{'lat'},$leftpt->{'direction'}) = great_circle_destination($refpt->{'lon'}, $pi/2-$refpt->{'lat'}, $offsetbrg, &m2rad(-$leftpt->{'offset'}));
        $leftmodelbrg=rad2deg($offsetbrg);
        $leftptlat=rad2deg($leftpt->{'lat'});
        $leftptlon=rad2deg($leftpt->{'lon'});
        print FILE "  <wpt lat='$leftptlat' lon='$leftptlon'><name>L $leftmodelbrg</name></wpt>\n" if $format eq "gpx";
        print FILE "OBJECT_SHARED ".$model." ".$leftptlon." ".$leftptlat." 0 0\n" if $format eq "stg";
        print "insert into fgs_objects values (DEFAULT,DEFAULT,DEFAULT,'$desc (W-$wayid L)',GeometryFromText('POINT($leftptlon $leftptlat)',4326),-9999,0,null,$leftmodelbrg,'$country',$model,1,$tile,$wayid,'$submitter',true,DEFAULT);\n" if $format eq "sql";
      };
      if ($output->{'right'}==1)
      {
        ($rightpt->{'lon'},$rightpt->{'lat'},$rightpt->{'direction'}) = great_circle_destination($refpt->{'lon'}, $pi/2-$refpt->{'lat'}, $offsetbrg, &m2rad($rightpt->{'offset'}));
        $rightmodelbrg=rad2deg($offsetbrg+$pi);
        $rightptlat=rad2deg($rightpt->{'lat'});
        $rightptlon=rad2deg($rightpt->{'lon'});        
        print FILE "  <wpt lat='$rightptlat' lon='$rightptlon'><name>R $rightmodelbrg</name></wpt>\n" if $format eq "gpx";
        print FILE "OBJECT_SHARED ".$model." ".$rightptlon."  ".$rightptlat." 0 0\n" if $format eq "stg";
        print "insert into fgs_objects values (DEFAULT,DEFAULT,DEFAULT,'$desc (W-$wayid R)',GeometryFromText('POINT($rightptlon $rightptlat)',4326),-9999,0,null,$rightmodelbrg,'$country',$model,1,$tile,$wayid,'$submitter',true,DEFAULT);\n" if $format eq "sql";
      };
    };
    $carryoffset=$refpt->{'offset'}-$distancem;
  };
};
print FILE "</gpx>\n" if $format eq "gpx";
close FILE if $format eq "gpx";
close FILE if $format eq "stg";
exit 0;
