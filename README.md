### Overview
Currently in the design and initial development phase, Emergence is a biological sequence annotation and analysis system designed to provide analysis, curation and data visualization all within the same package. It has a strong focus on integration of existing tools and frameworks over reinventing the wheel.

Emergence is written using [Python3](http://www.python.org) and the [Django web framework](https://www.djangoproject.com/) on the server-side, with a UI implemented using [AngularJS](http://angularjs.org/), HTML5, and CSS3. Its development has been guided by the needs of active projects in eukaryotic annotation, RNA-Seq, SNP analysis and metagenomics.

### First release targets
Progress will be continually committed here, and the next release target coinciding with its second presentation at [Genome Informatics 2013](http://meetings.cshl.edu/meetings/2013/info13.shtml) in late October. The target features for the next release include:

* Formalized tool dependency system with input/output type classifications
* Local command execution and monitoring
* Distributed command processing via [Grid Engine](http://www.oracle.com/us/products/tools/oracle-grid-engine-075549.html)
* [Galaxy](http://galaxyproject.org/) API integration layer
* [Ergatis](http://ergatis.sourceforge.net/) API integration layer
* Initial tool/pipeline support for:
  * Prokaryotic gene finders: Prodigal and Glimmer
  * Eukaryotic gene finders: Augustus and Genemark-ES
  * Digital read normalization (khmer analysis)
  * RNA-seq assembly: Trinity
  * SNP analysis pipeline (via Galaxy)
  * Prokaryotic structural and functional pipeline (via Ergatis)
  * Eukaryotic protein functional pipeline (via Ergatis)
  * Result visualization with [JBrowse](http://jbrowse.org/)

### Try out the current code
Although there isn't a packaged release yet, you can run through an example pipeline with the development version now. See the [Getting Started](https://github.com/jorvis/Emergence/blob/master/docs/getting_started.md) guide.
