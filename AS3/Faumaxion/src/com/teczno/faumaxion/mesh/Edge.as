package com.teczno.faumaxion.mesh
{
	public class Edge
	{
		public var vertexA:Vertex;
		public var vertexB:Vertex;
		public var triangleA:Triangle;
		public var triangleB:Triangle;
		public var kind:String;
		
		public function Edge(vertexA:Vertex, vertexB:Vertex, triangleA:Triangle, triangleB:Triangle, kind:String)
		{
			this.vertexA = vertexA;
			this.vertexB = vertexB;
			this.triangleA = triangleA;
			this.triangleB = triangleB;
			this.kind = kind;
		}
		
		public function triangles():Array
		{
			return [triangleA, triangleB];
		}
		
		public function matches(other:Edge):Boolean
		{
			if(vertexA == other.vertexA && vertexB == other.vertexB) {
				// same edge
				return true;
				
			} else if(vertexA == other.vertexB && vertexB == other.vertexA) {
				// same vertices, but reversed
				return true;

			} else {
				return false;
			}
		}
	}
}