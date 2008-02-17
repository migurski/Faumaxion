package com.teczno.faumaxion.mesh
{
	public class Triangle
	{
		public var edgeA:Edge;
		public var edgeB:Edge;
		public var edgeC:Edge;
		public var center:Vertex;
		
		public function Triangle(edgeA:Edge, edgeB:Edge, edgeC:Edge)
		{
			this.edgeA = edgeA;
			this.edgeB = edgeB;
			this.edgeC = edgeC;
			this.calculateCenter();
		}
		
		public function calculateCenter():void
		{
			if(edgeA && edgeB && edgeC) {
				var v:Array = vertices();
				
				var v1:Vertex = v[0] as Vertex;
				var v2:Vertex = v[1] as Vertex;
				var v3:Vertex = v[2] as Vertex;
				
				var avgX:Number = (v1.x + v2.x + v3.x) / 3;
				var avgY:Number = (v1.y + v2.y + v3.y) / 3;
				var avgZ:Number = (v1.z + v2.z + v3.z) / 3;
				
				var length:Number = Math.sqrt(avgX * avgX + avgY * avgY + avgZ * avgZ);
				center = new Vertex(avgX/length, avgY/length, avgZ/length);
			}
		}
		
		public function edges():Array
		{
			return [edgeA, edgeB, edgeC];
		}
		
		public function shared(other:Triangle):Edge
		{
			for each(var thisEdge:Edge in edges()) {
				for each(var otherEdge:Edge in other.edges()) {
					if(thisEdge.matches(otherEdge)) {
						return thisEdge;
					}
				}
			}
			
			return undefined;
		}
		
		public function neighbors():Array
		{
			var neighbors:Array = [];
			
			for each(var edge:Edge in edges()) {
				for each(var neighbor:Triangle in edge.triangles()) {
					if(neighbor != this) {
						neighbors.push(neighbor);
					}
				}
			}
			
			return neighbors;
		}
		
		public function vertices():Array
		{
			var eAvA:Vertex = this.edgeA.vertexA;
			var eAvB:Vertex = this.edgeA.vertexB;
			var eBvA:Vertex = this.edgeB.vertexA;
			var eBvB:Vertex = this.edgeB.vertexB;
			var eCvA:Vertex = this.edgeC.vertexA;
			var eCvB:Vertex = this.edgeC.vertexB;
			
			var v1:Vertex, v2:Vertex, v3:Vertex;
			
			if(eAvB == eBvA) {
				v1 = eAvA;
				v2 = eBvA;

			} else if(eAvB == eBvB) {
				v1 = eAvA;
				v2 = eBvB;

			} else if(eAvA == eBvA) {
				v1 = eAvB;
				v2 = eBvA;

			} else if(eAvA == eBvB) {
				v1 = eAvB;
				v2 = eBvB;
			}
			
			if(eBvB == eCvA) {
				v2 = eBvA;
				v3 = eCvA;

			} else if(eBvB == eCvB) {
				v2 = eBvA;
				v3 = eCvB;

			} else if(eBvA == eCvA) {
				v2 = eBvB;
				v3 = eCvA;

			} else if(eBvA == eCvB) {
				v2 = eBvB;
				v3 = eCvB;
			}
			
			return [v1, v2, v3];
		}
	}
}