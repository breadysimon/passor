var args = process.argv.slice(2);
var gherkinHtmlify = require('./gherkin-htmlify');
var featureDirectoryPath = args[0];//'/input';
var outputDirectory = args[1];//'/output/html';

var options = {
  mainTitle: "测试用例集"
};                                                                     
gherkinHtmlify.process(featureDirectoryPath, outputDirectory, options);
