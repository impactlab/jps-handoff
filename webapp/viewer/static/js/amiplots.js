function createHeatMap(id,data,w,h) {
  var n_intervals = 96;
  var n_days = data.length/n_intervals;

  var parseDate = d3.time.format("%Y-%m-%d").parse;
  var parseTime = d3.time.format("%H:%M").parse;

  data.forEach(function(d) {
    d.date = parseDate(d.date);
    d.time = parseTime(d.time);
    d.reading = +d.reading;
    return d;
  });

  var margin = {top: 20, right: 10, bottom: 70, left: 40},
    width = w - margin.left - margin.right,
    height = h - margin.top - margin.bottom;

  var x = d3.time.scale().range([0, width]),
    y = d3.time.scale().range([0, height]);

  var xAxis = d3.svg.axis().scale(x).orient("bottom"),
    yAxis = d3.svg.axis().scale(y).orient("left")
              .tickFormat(d3.time.format("%H:%M"));

  var svg = d3.select(id).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.bottom);

  /* with some overlap */
  var cell_width = 1.1 * width / n_days,
    cell_height = 1.1 * height / n_intervals;

  svg.append("rect")
    .attr("width", width + cell_width)
    .attr("height", height + cell_height)
    .attr("fill", "black")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var heatmap = svg.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  x.domain(d3.extent(data.map(function(d) { return d.date; })));
  y.domain(d3.extent(data.map(function(d) { return d.time; })));

  var colors = ["#a50026","#d73027","#f46d43","#fdae61","#fee08b","#ffffbf","#d9ef8b","#a6d96a","#66bd63","#1a9850","#006837"];
  var colorScale = d3.scale.quantile()
    .domain([0, d3.max(data.map(function(d) { return d.reading; }))])
    .range(colors);

  heatmap.selectAll(".row")
    .data(data)
    .enter().append("svg:rect")
    .attr("class", "cell")
    .attr("x", function(d) { return x(d.date) })
    .attr("y", function(d) { return y(d.time) })
    .attr("width", cell_width)
    .attr("height", cell_height)
    .style("fill", function(d) {
      return colorScale(d.reading);
    })
    .style("stroke","none")
    .append("svg:title")
    .text(function(d) { return d.reading + " kW"; });

  heatmap.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + (height + (height / n_intervals)) + ")")
    .call(xAxis);

  heatmap.append("g")
    .attr("class", "y axis")
    .call(yAxis);
}


/* D3 code for generation of brushable detail preview plot */

function createBrushAreaChart(id,data,evtdata,w,h) {

  var parseDate = d3.time.format("%Y-%m-%d %H:%M").parse;
  var parseDates = d3.time.format("%Y-%m-%d %H:%M:%S").parse;

  data.forEach(function(d) {
    d.date = parseDate(d.date);
    d.reading = +d.reading;
    return d;
  });

  evtdata.forEach(function(d) {
    d.date = parseDates(d.date);
    d.text = d.text;
    return d;
  });


  var margin = {top: 10, right: 20, bottom: 170, left: 50},
    margin2 = {top: h - 140, right: 20, bottom: 100, left: 50},
    margin3 = {top: h - 70, right: 20, bottom: 30, left: 50},
    width = w - margin.left - margin.right,
    height = h - margin.top - margin.bottom,
    height2 = h - margin2.top - margin2.bottom;
    height3 = h - margin3.top - margin3.bottom;

  var x = d3.time.scale().range([0, width]),
    x2 = d3.time.scale().range([0, width]),
    x3 = d3.time.scale().range([0, width]),
    y = d3.scale.linear().range([height, 0]),
    y2 = d3.scale.linear().range([height2, 0]);
    y3 = d3.scale.linear().range([height3, 0]);

  var xAxis = d3.svg.axis().scale(x).orient("bottom"),
    xAxis2 = d3.svg.axis().scale(x2).orient("bottom"),
    xAxis3 = d3.svg.axis().scale(x3).orient("bottom"),
    yAxis = d3.svg.axis().scale(y).orient("left");

  var brush = d3.svg.brush()
    .x(x3)
    .on("brush", brushed);

  var area = d3.svg.area()
    .interpolate("monotone")
    .x(function(d) { return x(d.date); })
    .y0(height)
    .y1(function(d) { return y(d.reading); });

  var area3 = d3.svg.area()
    .interpolate("monotone")
    .x(function(d) { return x3(d.date); })
    .y0(height3)
    .y1(function(d) { return y3(d.reading); });

  var svg = d3.select(id).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.bottom);

  svg.append("defs").append("clipPath")
    .attr("id", "clip")
    .append("rect")
    .attr("width", width)
    .attr("height", height);

  var focus = svg.append("g")
    .attr("class", "focus")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var evt = svg.append("g")
    .attr("class", "focus")
    .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");

  var context = svg.append("g")
    .attr("class", "context")
    .attr("transform", "translate(" + margin3.left + "," + margin3.top + ")");

  x.domain(d3.extent(data.map(function(d) { return d.date-1; })));
  y.domain([0, d3.max(data.map(function(d) { return d.reading; }))]);
  x2.domain(x.domain());
  y2.domain([0,1]);
  x3.domain(x.domain());
  y3.domain(y.domain());

  focus.append("path")
    .datum(data)
    .attr("class", "area")
    .attr("d", area);

  focus.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);

  focus.append("g")
    .attr("class", "y axis")
    .call(yAxis);

  svg.append("text")
    .attr("class", "y label")
    .attr("text-anchor", "end")
    .attr("y", 15)
    .attr("x", -40-height)
    .attr("transform", "rotate(-90)")
    .text("Events");

  svg.append("text")
    .attr("class", "y label")
    .attr("text-anchor", "end")
    .attr("y", 15)
    .attr("x", -80-height-height2)
    .attr("transform", "rotate(-90)")
    .text("Select");

  var tooltip = d3.select("body").append("div")
    .attr("class","tooltip").style("opacity",0);

  lines = evt.selectAll(".line")
    .data(evtdata)
    .enter()
    .append("line")
    .attr('class', 'line')
    .attr("stroke", "black")
    .attr("stroke-width", 3)
    .attr("x1", function(d) { return x2(d.date)})
    .attr("x2", function(d) { return x2(d.date)})
    .attr("y1", function(d) { return y2(0)})
    .attr("y2", function(d) { return y2(1)})
    .on("mouseover", function(d) {
      tooltip.transition()
        .duration(200)
        .style("opacity", .9);
      tooltip.html(d.text)
        .style("left", (d3.event.pageX+5) + "px")
        .style("top", (d3.event.pageY-28) + "px");
     })
     .on("mouseout", function(d) {
        tooltip.transition()
          .duration(500)
          .style("opacity", 0);
     });

  evt.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height2 + ")")
    .call(xAxis2);

  svg.append("text")
    .attr("class", "y label")
    .attr("text-anchor", "end")
    .attr("y", 15)
    .attr("x", -10)
    .attr("transform", "rotate(-90)")
    .text("Profile (kW)");

  context.append("path")
    .datum(data)
    .attr("class", "area")
    .attr("d", area3);

  context.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height3 + ")")
    .call(xAxis3);

  context.append("g")
    .attr("class", "x brush")
    .call(brush)
    .selectAll("rect")
    .attr("y", -6)
    .attr("height", height3 + 7);

  function brushed() {
    x.domain(brush.empty() ? x3.domain() : brush.extent());
    x2.domain(brush.empty() ? x3.domain() : brush.extent());
    evt.selectAll(".line")
      .attr("x1", function(d) { return x2(d.date)})
      .attr("x2", function(d) { return x2(d.date)});
    evt.select(".x.axis").call(xAxis2);
    focus.select(".area").attr("d", area);
    focus.select(".x.axis").call(xAxis);
  }
}
