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
		
		public function toPrettyString():String
		{
			var out:String = '';
			
			if(lat > 0) {
				out += lat.toFixed(2) + '°N';
				
			} else {
				out += Math.abs(lat).toFixed(2) + '°S';
			}
			
			out += ', ';
			
			if(lon > 0) {
				out += lon.toFixed(2) + '°E';
				
			} else {
				out += Math.abs(lon).toFixed(2) + '°W';
			}
			
			return out;
		}
	}
}