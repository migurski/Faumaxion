package com.teczno.faumaxion
{
	public class Location
	{
		public var lat:Number;
		public var lon:Number;
		
		public function Location(lat:Number, lon:Number)
		{
			this.lat = lat;
			this.lon = lon;
		}
		
		public function clone():Location
		{
			return new Location(lat, lon);
		}
		
		public function toString():String
		{
			return '(lat=' + lat.toFixed(3) + ', lon=' + lon.toFixed(3) + ')';
		}
	}
}