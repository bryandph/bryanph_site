var d3 = require("../node_modules/d3"),
    cloud = require("../node_modules/d3-cloud");

var layout = cloud()
    .size([400, 100])
    .words([
      "mentor", "pre-chewed", "incompetencies", "glutton", "sadist", "computer", "crime", "scandal", "underachiever", "dirt-cheap", "arrested", "conscience", "hacker", "baud", "three-piece", "spoon-feed", "bank", "tampering", "half-assing", "color", "hunger", "criminal", "tick", "hacker", "taste", "out smart", "electron", "refuge", "nationality", "cool", "screw", "kid", "pulse", "apathetic", "profiteer", "curiosity", "cheat", "vain", "copy", "bias", "addict", "smart", "teach", "day-to-day"].map(function(d) {
      return {text: d, size: 10 + Math.random() * 30, test: "haha"};
    }))
    .padding(2)
    .rotate(function() { return ~~(Math.random() * 2) * 90; })
    .font("Impact")
    .fontSize(function(d) { return d.size; })
    .on("end", draw);

layout.start();

function draw(words) {
  d3.select("#wordcloud").append("svg")
      .attr("width", "100%")
      // .attr("width", layout.size()[0])
      // .attr("height", layout.size()[1])
      .attr("viewBox", '0 0 400 100')
    .append("g")
      .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
    .selectAll("text")
      .data(words)
    .enter().append("text")
      .style("font-size", function(d) { return d.size + "px"; })
      .style("font-family", "inherit")
      .style('fill', 'White')
      .attr("text-anchor", "middle")
      .attr("transform", function(d) {
        return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
      })
      .text(function(d) { return d.text; });
}
