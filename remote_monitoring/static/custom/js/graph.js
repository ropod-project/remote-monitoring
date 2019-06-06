function showGraph(){
    var graph = d3.select("#graph")
        .append("svg")
        .attr("width", 200)
        .attr("height", 200);    

    var nodes = [
        {x: 10, y: 50},
        {x: 70, y: 10},
        {x: 140, y: 50}   
    ];
    var links = [
        {source: nodes[0], target: nodes[1]},
        {source: nodes[2], target: nodes[1]}
    ]

    console.log(graph);
    graph.selectAll("circle.nodes")
       .data(nodes)
       .enter()
       .append("svg:circle")
       .attr("cx", function(d) { return d.x; })
       .attr("cy", function(d) { return d.y; })
       .attr("r", "10px")
       .attr("fill", "black")
    graph.selectAll(".line")
       .data(links)
       .enter()
       .append("line")
       .attr("x1", function(d) { return d.source.x })
       .attr("y1", function(d) { return d.source.y })
       .attr("x2", function(d) { return d.target.x })
       .attr("y2", function(d) { return d.target.y })
       .attr('stroke', 'black').
       attr('stroke-width', 2);
       // .style({'stroke': 'black', 'stroke-width': '20px'});
               // , 'stroke-width':'2px'});

    console.log(graph);
}

function showForceGraph(){
    // hardcoded for testing
    var node_names = ['A', 'B', 'C'];
    var link_dict = [
        {'source':'A', 'target':'B'},
        {'source':'A', 'target':'C'}
    ];

    var data = getData(node_names, link_dict);
	var svg = d3.select("#graph").append("svg")
	var chartLayer = svg.append("g").classed("chartLayer", true)

	setSize(data, svg, chartLayer);
	drawChart(data, svg);
}

function getData(node_names, link_dict){
    var node_radius = 20 //pixels

    var nodes = [];
    for(i = 0; i<node_names.length; i++){
        nodes.push({label:node_names[i], r:node_radius});
    }
    var links = [];
    var node_dict = {};
    for(i=0; i<nodes.length; i++){ node_dict[nodes[i].label] = nodes[i]; }
    for(i=0; i < link_dict.length; i++){
        links.push({
            'source':node_dict[link_dict[i].source], 
            'target':node_dict[link_dict[i].target]
        });
    }
	var data = {
        'nodes':nodes,
        'links':links
	}
    return data;
}
    
function setSize(data, svg, chartLayer) {
    width = 500;
    height = 300;

	svg.attr("width", width).attr("height", height);

	chartLayer
		.attr("width", width)
		.attr("height", height)
		.attr("transform", "translate("+[0, 0]+")");
}
    
function drawChart(data, svg) {
    var link_distance = 30;
    var link_width = 5;
    var link_color = "black";
    var node_color = "lightblue";
    var node_outline_color = "black";
    var node_radius = 20;

	var simulation = d3.forceSimulation()
		.force("link", d3.forceLink().id(function(d) { return d.label }))
		.force("collide",d3.forceCollide( function(d){return d.r + link_distance }).iterations(16) )
		.force("charge", d3.forceManyBody())
		.force("center", d3.forceCenter(width / 2, height / 2))
		.force("y", d3.forceY(0))
		.force("x", d3.forceX(0));

    svg.append("defs").append("marker")
        .attr("id", "arrowHead")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 25)
        .attr("refY", 0)
        .attr("markerWidth", 3)
        .attr("markerHeight", 5)
        .attr("orient", "auto")
        .append("svg:path")
        .attr("d", "M0,-5L15,0L0,5")
        .attr("fill", link_color)
        .attr("stroke", link_color);

    var link = svg.append("g")
		.attr("class", "links")
		.selectAll("line")
		.data(data.links)
		.enter()
		.append("line")
        .attr("marker-end", "url(#arrowHead)")
		.attr("stroke", link_color)
        .attr("stroke-width", link_width);

    var node = svg.append("g")
		.attr("class", "nodes")
		.selectAll("circle")
		.data(data.nodes)
		.enter().append("circle")
		.attr("r", function(d){  return node_radius })
        .attr("stroke", node_outline_color)
        .attr("fill", node_color)
		.call(d3.drag()
				.on("start", dragstarted)
				.on("drag", dragged)
				.on("end", dragended));    

	var ticked = function() {
		link
			.attr("x1", function(d) { return d.source.x; })
			.attr("y1", function(d) { return d.source.y; })
			.attr("x2", function(d) { return d.target.x; })
			.attr("y2", function(d) { return d.target.y; });

		node
			.attr("cx", function(d) { return d.x; })
			.attr("cy", function(d) { return d.y; });
        text
            .attr("transform", function(d) {return "translate(" + d.x + "," + d.y + ")"; });
	}  

	simulation
		.nodes(data.nodes)
		.on("tick", ticked);

	simulation.force("link")
		.links(data.links);    

    var text = svg.append("g").selectAll("text")
        .data(simulation.nodes())
        .enter().append("text")
        .attr("x", node_radius+5)
        .attr("y", node_radius+5)
        .text(function(d) { return d.label; });

	function dragstarted(d) {
		if (!d3.event.active) simulation.alphaTarget(0.3).restart();
		d.fx = d.x;
		d.fy = d.y;
	}

	function dragged(d) {
		d.fx = d3.event.x;
		d.fy = d3.event.y;
	}

	function dragended(d) {
		if (!d3.event.active) simulation.alphaTarget(0);
		d.fx = null;
		d.fy = null;
	} 

}
