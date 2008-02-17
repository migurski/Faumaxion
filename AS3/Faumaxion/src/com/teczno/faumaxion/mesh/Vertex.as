package com.teczno.faumaxion.mesh
{
	public class Vertex
	{
		public var x:Number;
		public var y:Number;
		public var z:Number;

		public function Vertex(x:Number, y:Number, z:Number)
		{
			this.x = x;
			this.y = y;
			this.z = z;
		}
		
		public function clone():Vertex
		{
			return new Vertex(x, y, z);
		}
		
		public function distance(other:Vertex):Number
		{
			var diff:Vertex = new Vertex(other.x - x, other.y - y, other.z - z);
			return Math.sqrt(diff.x * diff.x + diff.y * diff.y + diff.z * diff.z);
		}
		
		public function midpoint(other:Vertex):Vertex
		{
			return new Vertex((x + other.x)/2, (y + other.y)/2, (z + other.z)/2);
		}
	}
}