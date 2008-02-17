package com.teczno.faumaxion.icosahedron
{
	import com.teczno.faumaxion.Gnomonic;
	import com.teczno.faumaxion.Location;
	import com.teczno.faumaxion.Transformation;
	import com.teczno.faumaxion.mesh.*;
	
	import flash.geom.Point;

	public class Face extends Triangle
	{
		public var path:String;
		public var transform:Transformation;
		
		public static const SIDE:Number = 256;
		
		// Refers to the projected, two-dimensional length
		private static const AVERAGE_EDGE_LENGTH:Number = 1.323169076499213670;
		
		// to be populated by faces() below
		private static var FACES:Array;

		public function Face(edgeA:Edge, edgeB:Edge, edgeC:Edge, path:String)
		{
			super(edgeA, edgeB, edgeC);
			
			this.path = path;
			
			transform = new Transformation(1/AVERAGE_EDGE_LENGTH, 0, 0,
			                               0, -1/AVERAGE_EDGE_LENGTH, 0);
		}
		
		public function centerLocation():Location
		{
			return vertex2location(center);
		}
		
		public function projectVertex(vertex:Vertex):Point
		{
			return projectLocation(vertex2location(vertex));
		}
		
		public function projectLocation(location:Location):Point
		{
			return transform.apply(Gnomonic.project(location, centerLocation()));
		}
		
		public function unprojectPoint(point:Point):Location
		{
			return Gnomonic.unproject(transform.unapply(point), centerLocation());
		}
		
		public function adjoin(other:Face):void
		{
			var edge:Edge = shared(other);
			
			// 2D positions of vertices in other projection
			var a1:Point = other.projectVertex(edge.vertexA);
			var b1:Point = other.projectVertex(edge.vertexB);
			var c1:Point = deriveThirdPoint(a1, b1);
			
			// 2D positions of vertices in this projection
			var a2:Point = projectVertex(edge.vertexA);
			var b2:Point = projectVertex(edge.vertexB);
			var c2:Point = deriveThirdPoint(a2, b2);
			
			var t:Transformation = Transformation.deriveTransformation(a1, a2, b1, b2, c1, c2);
			other.transform = other.transform.multiply(t);
		}
		
		public function arrangeNeighbors(preferredKind:String='LAND'):Array
		{
			var seen:Array = [];
			var remain:Array = [{sort: 9999, face: this, chain: []}];
			var kindWeights:Object;
			
			if(preferredKind == 'LAND') {
				kindWeights = {LAND: 0, WATER: 2};

			} else if(preferredKind == 'WATER') {
				kindWeights = {WATER: 0, LAND: 2};
			}
			
			while(remain.length) {
				remain.sortOn('sort', Array.NUMERIC);
				var top:Object = remain.shift();
				var face:Face = top['face'] as Face;
				var chain:Array = top['chain'] as Array;
				
				if(seen.indexOf(face) >= 0) {
					continue;
					
				} else {
					seen.push(face);
				}
				
				if(chain.length) {
					(chain[chain.length - 1] as Face).adjoin(face);
				}
				
				chain = chain.slice();
				chain.push(face);
				
				for each(var neighbor:Face in face.neighbors()) {
					var edge:Edge = face.shared(neighbor);
					remain.push({sort: (kindWeights[edge.kind] as Number) + chain.length, face: neighbor, chain: chain});
				}
			}
			
			return seen;
		}
		
		public function orientNorth(location:Location):void
		{
			var p1:Point = projectLocation(location);
			var p2:Point = projectLocation(new Location(location.lat + 1, location.lon));
			
			// -90 deg is the desired rotation
			var theta:Number = Math.atan2(p2.y - p1.y, p2.x - p1.x);
			var angle:Number = -90 - Gnomonic.rad2deg(theta);
			
			rotate(angle);
		}
		
		public function centerOn(location:Location):void
		{
			var p:Point = projectLocation(location);
			translate(-p.x, -p.y);
		}
		
		public function rotate(angle:Number=0):void
		{
			var theta:Number = Gnomonic.deg2rad(angle);
			var t:Transformation = new Transformation(Math.cos(theta), -Math.sin(theta), 0, Math.sin(theta), Math.cos(theta), 0);
			transform = transform.multiply(t);
		}
		
		public function translate(xdistance:Number=0, ydistance:Number=0):void
		{
			var t:Transformation = new Transformation(1, 0, xdistance, 0, 1, ydistance);
			transform = transform.multiply(t);
		}
		
		public function scale(factor:Number=1):void
		{
			var t:Transformation = new Transformation(factor, 0, 0, 0, factor, 0);
			transform = transform.multiply(t);
		}
		
		public static function location2vertex(location:Location):Vertex
		{
			if(location.lon < 0) {
				location.lon += 360;
			}
			
			var theta:Number = Gnomonic.deg2rad(90 - location.lat);
			var phi:Number = Gnomonic.deg2rad(location.lon);
			
			var x:Number = Math.sin(theta) * Math.cos(phi);
			var y:Number = Math.sin(theta) * Math.sin(phi);
			var z:Number = Math.cos(theta);
			
			return new Vertex(x, y, z);
		}
		
		public static function vertex2location(vertex:Vertex):Location
		{
			var a:Number, phi:Number;
			
			if(vertex.x > 0 && vertex.y > 0)
				a = Gnomonic.deg2rad(0);
				
			if(vertex.x < 0 && vertex.y > 0)
				a = Gnomonic.deg2rad(180);
				
			if(vertex.x < 0 && vertex.y < 0)
				a = Gnomonic.deg2rad(180);
				
			if(vertex.x > 0 && vertex.y < 0)
				a = Gnomonic.deg2rad(360);
				
			if(vertex.x == 0 && vertex.y > 0)
				phi = Gnomonic.deg2rad(90);
				
			if(vertex.x == 0 && vertex.y < 0)
				phi = Gnomonic.deg2rad(270);
				
			if(vertex.x > 0 && vertex.y == 0)
				phi = Gnomonic.deg2rad(0);
				
			if(vertex.x < 0 && vertex.y == 0)
				phi = Gnomonic.deg2rad(180);
				
			if(vertex.x != 0 && vertex.y != 0)
				phi = Math.atan(vertex.y / vertex.x) + a;
			
			var theta:Number = Math.acos(vertex.z);
			return new Location(90 - Gnomonic.rad2deg(theta), Gnomonic.rad2deg(phi));
		}
		
		public static function vertex2face(vertex:Vertex):Face
		{
			var face:Face;
			var distances:Array = [];
			
			for each(face in World.faces()) {
				distances.push([vertex.distance(face.center), face]);
			}
			
			distances.sort();
			
			return distances[0][1] as Face;
		}

		public static function deriveThirdPoint(p1:Point, p2:Point):Point
		{
			// a vector from a to b
			var p3:Point = new Point(p2.x - p1.x, p2.y - p1.y);
			var theta:Number = Math.atan2(p3.y, p3.x);
			
			// two more unit-length vectors, one for each leg of the equilateral right triangle
			var leg1:Point = new Point(Math.cos(theta + Math.PI/4), Math.sin(theta + Math.PI/4));
			var leg2:Point = new Point(Math.cos(theta + 3*Math.PI/4), Math.sin(theta + 3*Math.PI/4));
			
			// slope and intercept for each line
			// intercept derived from http://mathworld.wolfram.com/Line.html (2)
			var slope1:Number = leg1.y / leg1.x;
			var intercept1:Number = p1.y - slope1 * p1.x;
			var slope2:Number = leg2.y / leg2.x;
			var intercept2:Number = p2.y - slope2 * p2.x;
			
			// solve for x and y of the third point
			p3.x = (intercept2 - intercept1) / (slope1 - slope2);
			p3.y = slope1 * p3.x + intercept1;
			
			return p3;
		}
	}
}
