package com.teczno.faumaxion
{
	import flash.geom.Point;
	
	public class Gnomonic
	{
		public static function deg2rad(degrees:Number):Number
		{
			return degrees * Math.PI / 180;
		}
		
		public static function rad2deg(radians:Number):Number
		{
			return radians * 180 / Math.PI;
		}
		
		public static function project(location:Location, center:Location):Point
		{
			var lat:Number = deg2rad(location.lat);
			var lon:Number = deg2rad(location.lon);
			var lat0:Number = deg2rad(center.lat);
			var lon0:Number = deg2rad(center.lon);
			
			var cosC:Number = Math.sin(lat0) * Math.sin(lat) + Math.cos(lat0) * Math.cos(lat) * Math.cos(lon - lon0);
			
			var x:Number = Math.cos(lat) * Math.sin(lon - lon0) / cosC;
			var y:Number = (Math.cos(lat0) * Math.sin(lat) - Math.sin(lat0) * Math.cos(lat) * Math.cos(lon - lon0)) / cosC;
			
			return new Point(x, y);
		}
		
		public static function unproject(point:Point, center:Location):Location
		{
			var lat0:Number = deg2rad(center.lat);
			var lon0:Number = deg2rad(center.lon);
			
			var p:Number = Math.sqrt(point.x * point.x + point.y * point.y);
			var c:Number = Math.atan(p);
			
			if(p == 0) {
				// avoid divide-by-zero later
				return center.clone();
			}
			
			var lat:Number = Math.asin(Math.cos(c) * Math.sin(lat0) + (point.y * Math.sin(c) * Math.cos(lat0)) / p);
			var lon:Number = lon0 + Math.atan2(point.x * Math.sin(c), (p * Math.cos(lat0) * Math.cos(c) - point.y * Math.sin(lat0) * Math.sin(c)));
			
			return new Location(rad2deg(lat), rad2deg(lon));
		}
	}
}
