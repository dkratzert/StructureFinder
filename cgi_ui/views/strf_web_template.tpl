<!DOCTYPE HTML>
<html lang="en" xmlns="http://www.w3.org/1999/html">
<head>
    <meta charset="UTF-8">
    <title>StructureFinder</title>

    <link rel="stylesheet" href="http://{{my_ip}}/static/w2ui/w2ui-1.4.3.min.css">
    <link rel="stylesheet" href="http://{{my_ip}}/static/bootstrap-3.3.7/css/bootstrap.min.css">
    <link rel="stylesheet" href="http://{{my_ip}}/static/bootstrap-3.3.7/css/bootstrap-theme.min.css">
    <script src="http://{{my_ip}}/static/jquery/jquery-3.2.1.min.js"></script>
    <script src="http://{{my_ip}}/static/bootstrap-3.3.7/js/bootstrap.min.js"></script>
    <script src="http://{{my_ip}}/static/jsmol/JSmol_dk.nojq.lite.js"></script>
    <script src="http://{{my_ip}}/static/w2ui/w2ui-1.4.3.min.js"></script>
    <script src="http://{{my_ip}}/static/clipboard/clipboard.min.js"></script>
    <script src="http://{{my_ip}}/static/strf_web.js"></script>
    <script> 
        var cgifile = 'http://{{my_ip}}';
    </script>

<style type="text/css">

    body {
        /*background-color: #ffffff;*/
        font-size: 12px;
        line-height: inherit;
    }
    
    .border-right {
        border-right: 1px solid #bcbcbc;
    }
    
    .collapsing {
        transition: 1ms;
    }
    
    #resitable1 tr td {
        line-height: 13px;
        height: 13px;
        overflow: auto;
    }
    
    #resitable2 tr td {
        line-height: 13px;
        height: 13px;
        overflow: auto;
    }
    
    .btn-group {
        padding-bottom: 4px;
        padding-top: 4px;
    }
    
    .input-group {
        padding-bottom: 2px;
        padding-top: 2px;
    }
    
    .input-group-addon {
        min-width:75px;
        text-align:left;
    }
    
    #resfile {
        font-family: "Bitstream Vera Sans Mono", Monaco, "Courier New", Courier, monospace;
    }
    
    #jsmolcolumn {
        margin-right: 15px;
        margin-left: 15px;
        width: 360px;
        height: 320px;
}

</style>


</head>

<body>

<!-- "dropZone" adds drag&drop support for the web site -->
<div class="container" id="dropZone">
<h2>StructureFinder</h2>


<a type="button" class="btn btn-primary btn-sm" data-toggle="collapse" data-target="#adv-search"
        id="toggle_advsearch-button">Advanced Search</a>
<a type="button" class="btn btn-warning btn-sm" id="all_structures">Show All</a>
<a type="button" class="btn btn-default btn-sm invisible" id="cellsearchcsd_button" 
   href="http://{{my_ip}}/csd" target="_blank">CellCheckCSD</a>

<!-- ------------  The collapsible for simple search options: -----------------  -->
<div class="form-group row" id="mainsearch">
    <div class="col-sm-6">
        <div class="input-group input-group-sm">
            <span class="input-group-addon" data-toggle="tooltip" title="Search for a Unit Cell">Unit Cell</span>
            <input type="text" class="form-control" placeholder="a  b  c  &alpha;  &beta;  &gamma;    (or drag&drop .p4p, .res, cif file)" style="font-style: italic" id="smpl_cellsrch" name="cell">
            <div class="input-group-sm input-group-btn">
            <button class="btn btn-default" type="submit" id="smpl_cellsrchbutton">
                <i class="glyphicon glyphicon-search"></i>
            </button>
            </div>
        </div>
    </div>
    <div class="col-sm-6">
        <div class="input-group input-group-sm">
            <span class="input-group-addon" data-toggle="tooltip" title="Search for a Unit Cell">Text</span>
            <input type="text" class="form-control" placeholder="Search Text" id="smpl_textsrch" name="text">
            <div class="input-group-sm input-group-btn">
                <button class="btn btn-default" type="submit" id="smpl_textsrchbutton">
                    <i class="glyphicon glyphicon-search"></i>
                </button>
            </div>
        </div>
    </div>
</div>
<!-- ---------------------    End of simple search     ----------------------    -->


<!-- The collapsible for Advanced search options: -->
<div id="adv-search" class="collapse">
    <div class="row">
        <div class="col-sm-12">
            <div class="btn-group btn-group-sm" role="group">
                <a href="#" class="badge" id="more_info_badge">info</a> &nbsp;&nbsp;&nbsp;
                <input title="More cell search results" class="checkbox-inline" type="checkbox" value="" id="more_results">More cell search results &nbsp;&nbsp;&nbsp;
                <input title="Find supercells" type="checkbox" class="checkbox-inline" value="" id="supercells">Find supercells &nbsp;&nbsp;&nbsp;
                {{!space_groups}} Find by space group
            </div>
        </div>
    </div>

    <div id="more-cell-info" class="collapse">
        <div class="row">
            <div class="col-sm-6">
                <b>regular</b><br>
                volume: &plusmn;3 %, length: 0.06&nbsp;&angst;, angle: 1.0&deg;<br>
                <br>
                <b>more results option</b><br>
                volume: &plusmn;9 &percnt;, length: 0.2&nbsp;&angst;, angle: 2.0&deg;<br>
            </div>
            <div class="col-sm-6">
                <b>Supercells</b>
                <br>
                Find also unit cells of 1, 2, 3, 4, 6, 8, 10 times the volume.
                <br>
                <b>Space group search</b>
                <br>
                Be aware that not every cif file before SHELXL-2013 has a space group number. These will not be found.
            </div>
        </div>
    </div>

    <div class="row">
        <div class="column col-xs-6">
            <div class="input-group input-group-sm">
                <span class="input-group-addon">Uni Cell</span>
                <input type="text" class="form-control form-sm" style="font-style: italic" placeholder="a b c &alpha; &beta; &gamma;" id="cell_adv">
            </div>
        </div>
        <div class="column col-md-6">
            <div class="input-group input-group-sm w2ui-field">
                <span class="input-group-addon" data-toggle="tooltip"
                      title="Search for structures that were modified between two dates">Date from</span>
                <input class="input-sm" title="Date" type="text" id="date1" style="width: 95%">
                <span class="input-group-addon">to</span>
                <input class="input-sm" title="Date" type="text" id="date2" style="width: 95%">
                <a type="button" class="input-group-addon"
                   data-toggle="tooltip" title="Search for structures modified during the last month."
                   id="lastmsearchlink"> From Last Month</a>
            </div>
        </div>

        <script>
            var d1 = $('input[id=date1]');
            d1.w2field('date', {
                format: 'yyyy-mm-dd',
                end: d1
            });
            $('input[id=date2]').w2field('date', {
                format: 'yyyy-mm-dd',
                start: d1
            });
        </script>
    </div>

    <div class="row">
        <div class="column col-xs-6">
            <div class="input-group input-group-sm input-group-prepend has-success">
                <span class="input-group-addon" data-toggle="tooltip" title="should contain">Elements</span>
                <input type="text" class="form-control form-sm" placeholder="C H O ... (should contain)"
                       pattern="^[A-z]{1,}$" id="elements_in">
            </div>
        </div>
        <div class="column col-xs-6">
            <div class="input-group input-group-sm has-error">
                <span class="input-group-addon" data-toggle="tooltip" title="should not contain">Elements</span>
                <input type="text" class="form-control form-sm" placeholder="C H O ... (should not contain)"
                       pattern="^[A-z]{1,}$" id="elements_out">
            </div>
        </div>
    </div>

    <div class="row">
        <div class="column col-xs-6">
            <input class="checkbox-inline" type="checkbox" aria-label="Only these elements" 
                   title="Only above Elements" id="onlythese_elem">Only above Elements
        </div>
        <div class="column col-xs-6">
        </div>
    </div>
    
    <div class="row">
        <div class="column col-xs-6">
            <div class="input-group input-group-sm has-success">
                <span class="input-group-addon" data-toggle="tooltip" title="should contain">Text</span>
                <input type="text" class="form-control form-sm" placeholder="should contain" id="text_in">
            </div>
        </div>
        <div class="column col-xs-6">
            <div class="input-group input-group-sm has-error">
                <span class="input-group-addon" data-toggle="tooltip" title="should not contain">Text</span>
                <input type="text" class="form-control form-sm" placeholder="should not contain" id="text_out">
            </div>
        </div>
    </div>

    <div class="row">
        <div class="column col-xs-12">
            <a type="button" class="btn btn-sm btn-success" id="advsearch-button" style="min-width:90px"> Search </a>
        </div>
    </div>

<br>
</div>

<!-- End of collapsible for search options. -->
<div class="row">
    <div class="column col-lg-12">
        <div id="mygrid" style="height: 450px"></div>
    </div>
    <div class="column col-lg-12">
        <div class="panel panel-default">
            <div class="panel-body">
                <span class="invisible btn-group" id="cellrow" style="font-size: 14px"> </span>
                <span class="btn btn-default glyphicon glyphicon-copy invisible" id="cell_copy_btn"
                      data-toggle="tooltip" title="Copy cell to clipboard." data-clipboard-target="#hidden-cell">
                </span>
                <span class="btn-group invisible" id="growCheckBoxgroup">
                        &nbsp;&nbsp;&nbsp;&nbsp;
                        <input type="checkbox" title="Grow Structure" value="false" id="growCheckBox">Grow Structure
                </span>
            </div>
        </div>
    </div>
</div>


<div class="row">
    <div class="column col-md-4 panel panel-default invisible" id="jsmolcolumn"
         data-toggle="tooltip" title="Asymmetric Unit"> </div>
    <div class="column col-md-4" id="residualstable1"> </div>
    <div class="column col-md-4" id="residualstable2"> </div>
</div>


<div class="row">
    <div class="col-sm-10">
        <span id="residuals"></span>
    </div>
    <div class="col-sm-2">

    </div>
</div>

<address>
    <strong><a href="https://www.xs3.uni-freiburg.de/research/structurefinder">StructureFinder</a> 
        <span id="version"></span> by Daniel Kratzert</strong><br>
  <a href="mailto:daniel.kratzert@ac.uni-freiburg.de">daniel.kratzert@ac.uni-freiburg.de</a>
</address>

</div>  <!-- End of the main container div -->


</body>



</html>
