<!DOCTYPE HTML>
<html lang="en" xmlns="http://www.w3.org/1999/html">
<head>
    <title>StructureFinder</title>

    <link rel="stylesheet" href="http://{{my_ip}}/static/w2ui/w2ui-1.4.min.css">
    <link rel="stylesheet" href="http://{{my_ip}}/static/bootstrap-3.3.7/css/bootstrap.min.css">
    <link rel="stylesheet" href="http://{{my_ip}}/static/bootstrap-3.3.7/css/bootstrap-theme.min.css">
    <script src="http://{{my_ip}}/static/jquery/jquery-3.2.1.min.js"></script>
    <script src="http://{{my_ip}}/static/bootstrap-3.3.7/js/bootstrap.min.js"></script>
    <script src="http://{{my_ip}}/static/jsmol/JSmol_dk.nojq.lite.js"></script>
    <script src="http://{{my_ip}}/static/w2ui/w2ui-1.4.min.js"></script>
    <script src="http://{{my_ip}}/static/clipboard/clipboard.min.js"></script>


<style type="text/css">

body {
    /*background-color: #ffffff;*/
    font-size: 12px;
    line-height: inherit;
}

.border-right {
    border-right: 1px solid #bcbcbc;
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
    min-width:55px;
    text-align:left;
}

#jsmolcolumn {
    margin-right: 15px;
    margin-left: 15px;
    width: 360px;
    height: 320px;
}

</style>


<script>
var cgifile = 'http://{{my_ip}}';

// height of cif list to 35% of the screen height:
$(document).ready(function(){
    //gets the window's height
    var b = $(window).height();
    var h = b * 0.35;
    $("#mygrid").css("height", h);
});

$(document).ready(function(){
    $('[data-toggle="cell_tooltip"]').tooltip();
});

</script>


</head>

<body>


<div class="container">
<h2>StructureFinder</h2>


<a type="button" class="btn btn-default btn-xs" data-toggle="collapse" data-target="#adv-search"
        id="toggle_advsearch-button">Advanced Search</a>

<!-- ------------  The collapsible for simple search options: -----------------  -->
<div class="form-group row" id="mainsearch">
    <div class="col-sm-6">
        <div class="input-group input-group-sm">
            <span class="input-group-addon" data-toggle="tooltip" title="Search for a Unit Cell">Unit Cell</span>
            <input type="text" class="form-control" placeholder="a b c &alpha; &beta; &gamma;" style="font-style: italic" id="smpl_cellsrch" name="cell">
                <div class="input-group-sm input-group-btn">
                <button class="btn btn-default" type="submit" id="smpl_cellsrchbutton">
                    <i class="glyphicon glyphicon-search"></i>
                </button>
                </div>
            </input>
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
            </input>
        </div>
    </div>
</div>
<!-- ---------------------    End of simple search     ----------------------    -->
<div id="more-cell-info" class="collapse">
    <div class="row">
        <div class="col-sm-6">
            <b>regular</b><br>
            volume: &plusmn;3%, length: 0.001&nbsp;&angst;, angle: 1&deg;<br>
            <br>
            <b>more results option</b><br>
            volume: &plusmn;8&percnt;, length: 0.09&nbsp;&angst;, angle: 1.8&deg;<br>
        </div>
        <div class="col-sm-6">
            <b>Sub- and Supercells</b>
            <br>
            Find also unit cells of 0.25, 0.5, 1, 2, 3, 4 the volume.
        </div>
    </div>
</div>
<!-- The collapsible for Advanced search options: -->
<div id="adv-search" class="collapse">

    <div class="row">
        <div class="col-xs-12">
        <div class="btn-group btn-group-xs" role="group">
            <label><input type="checkbox" id="more_results"> More cell search results </label>
            <a href="#"><span class="label label-default" id="more_info_badge">info</span></a> &nbsp;&nbsp;&nbsp;
            <label><input type="checkbox" id="supercells"> Find sub- and supercells</label>
        </div>
        </div>
    </div>

    <div class="row">
        <div class="column col-xs-6">
            <div class="input-group input-group-sm has-success advsearchfields">
                <span class="input-group-addon" data-toggle="tooltip" title="should contain">Elements</span>
                <input type="text" class="form-control form-sm" placeholder="C H O ... (should contain)" id="elements_in">
            </div>
        </div>
        <div class="column col-xs-6">
            <div class="input-group input-group-sm has-error advsearchfields">
                <span class="input-group-addon" data-toggle="tooltip" title="should not contain">Elements</span>
                <input type="text" class="form-control form-sm" placeholder="C H O ... (should not contain)" id="elements_out">
            </div>
        </div>
    </div>
    <div class="row">
        <div class="column col-xs-6">
            <div class="input-group input-group-sm has-success advsearchfields">
                <span class="input-group-addon" data-toggle="tooltip" title="should contain">Text</span>
                <input type="text" class="form-control form-sm" placeholder="should contain" id="text_in">
            </div>
        </div>
        <div class="column col-xs-6">
            <div class="input-group input-group-sm has-error advsearchfields">
                <span class="input-group-addon" data-toggle="tooltip" title="should not contain">Text</span>
                <input type="text" class="form-control form-sm" placeholder="should not contain" id="text_out">
            </div>
        </div>
    </div>
    <div class="row">
        <div class="column col-xs-6">
            <div class="input-group input-group-sm advsearchfields">
                <span class="input-group-addon">Uni Cell</span>
                <input type="text" class="form-control form-sm" style="font-style: italic" placeholder="a b c &alpha; &beta; &gamma;" id="cell_adv">
            </div>
        </div>
        <div class="column col-md-6">
            <div class="input-group input-group-sm w2ui-field advsearchfields">
                <span class="input-group-addon" data-toggle="tooltip"
                      title="Search for structures that were modified between two dates">Date from</span>
                <input class="input-sm" type="text" id="date1">
                <span class="input-group-addon">to</span>
                <input class="input-sm" type="text" id="date2">
                <a type="button" class="btn btn-sm btn-standard input-group-addon"
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
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="column col-md-4 panel panel-default invisible" id="jsmolcolumn"
         data-toggle="tooltip" title="Asymmetric Unit">
    </div>
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
  <strong>StructureFinder by Daniel Kratzert</strong><br>
  <a href="mailto:daniel.kratzert@ac.uni-freiburg.de">daniel.kratzert@ac.uni-freiburg.de</a>
</address>

</div>  <!-- End of the main container div -->


</body>

<!-- Javascript functions start here: -->
<script>

jQuery(document).ready(function($) {
    // Do advanced search:
    var advanced_search_button = $("#advsearch-button");
    advanced_search_button.click(function(event) {
        var txt_in = document.getElementById("text_in").value;
        var txt_out = document.getElementById("text_out").value;
        var elements_in = document.getElementById("elements_in").value;
        var elements_out = document.getElementById("elements_out").value;
        var cell_adv = document.getElementById("cell_adv").value;
        var more_res = $('#more_results').is(':checked');
        var supercell = $('#supercells').is(':checked');
        var datefield1 = document.getElementById("date1").value;
        var datefield2 = document.getElementById("date2").value;
        advanced_search(txt_in, txt_out, elements_in, elements_out, cell_adv, more_res, supercell, datefield1, datefield2);
    });

    // Toggle search info:
    var more_info_button = $('#more_info_badge');
    more_info_button.click(function(){
        var button_text = more_info_button.text();
        $("#more-cell-info").toggle("fast", "swing");
    });

    // Switch between advanced and simple search:
    var advbutton = $('#toggle_advsearch-button');
    advbutton.click(function(){
        var button_text = advbutton.text();
        $("#mainsearch").toggle("fast", "swing");
        if (button_text.split(" ")[0] === "Advanced") {
            advbutton.html("Simple Search");
        } else {
            advbutton.html("Advanced Search");
        }
    });

    // Text search Button clicked:
    $("#smpl_textsrchbutton").click(function(event) {
        var txt = document.getElementById("smpl_textsrch").value;
        txtsearch(txt);
        //console.log(txt);
    });

    // Cell search Button clicked:
    $("#smpl_cellsrchbutton").click(function(event) {
        var cell = document.getElementById("smpl_cellsrch").value;
        cellsearch(cell);
    });

    // Enter key pressed in the simple text search field:
    $('#smpl_textsrch').keypress(function(e) {
        if (e.which === 13) {  // enter key
            var txt = document.getElementById("smpl_textsrch").value;
            txtsearch(txt);
            //console.log(txt);
        }
    });

    // Enter key pressed in the simple cell search field:
    $('#smpl_cellsrch').keypress(function(e) {
        if (e.which === 13) {  // enter key
            var cell = document.getElementById("smpl_cellsrch").value;
            cellsearch(cell);
            //console.log(cell);
        }
    });

    // Enter key pressed in one of the advanced search fields:
    $('.advsearchfields').keypress(function(e) {
        if (e.which === 13) {  // enter key
            advanced_search_button.click();
            //console.log(cell);
        }
    });

    // The main structures table:
    $('#mygrid').w2grid({
        name: 'mygrid',
        header: 'StructureFinder',
        url: cgifile+"/all",
        method: 'GET',
        show: {
            toolbar: false,
            footer: true
        },
        columns: [
            {field: 'recid',    caption: 'ID',        size: '45px', sortable: false, attr: 'align=center'},
            {field: 'filename', caption: 'filename',  size: '20%',  sortable: false, resizable: true},
            {field: 'dataname', caption: 'dataname',  size: '15%',  sortable: false, resizable: true},
            {field: 'path',     caption: 'directory', size: '65%',  sortable: false, resizable: true}
        ],
        searches: [
            {field: 'filename', caption: 'filename', type: 'text'},
            {field: 'dataname', caption: 'dataname', type: 'text'},
            {field: 'path', caption: 'directory', type: 'text'}
        ],
        //sortData: [{field: 'dataname', direction: 'ASC'}],
        onSelect:function(event) {
            showprop(event.recid);
            //console.log(record);
        }
    });


    function showprop(idstr) {
        /* This function uses AJAX POST calls to get the data of a structure and displays the below the main table. */
        // Get residuals table 1:
        $.post(url = cgifile, data = {id: idstr, residuals1: true}, function (result) {
            document.getElementById("residualstable1").innerHTML = result;
        });

        // Get residuals table 2:
        $.post(url = cgifile, data = {id: idstr, residuals2: true}, function (result) {
            document.getElementById("residualstable2").innerHTML = result;
        });

        // Get molecule data and display the molecule:
        var jsmolcol = $("#jsmolcolumn");
        $.post(url = cgifile+'/molecule', data = {id: idstr}, function (result) {
            Jmol._document = null;
            Jmol.getTMApplet("jmol", Info);
            jsmolcol.html(jmol._code);
            jmol.__loadModel(result);
            jsmolcol.removeClass('invisible');
            var tbl = $('#residualstable2');
            jsmolcol.css("height", tbl.height()-20);
        });

        // Get unit cell row:
        $.post(url = cgifile, data = {id: idstr, unitcell: true}, function (result) {
            $("#cellrow").removeClass('invisible');
            $("#cell_copy_btn").removeClass('invisible');
            document.getElementById("cellrow").innerHTML = result;

            var clipboard = new Clipboard('.btn');
            clipboard.on('success',
                function(e) {
                    e.clearSelection();
                }
            );
        });

        // display the big cif data table:
        $.post(url = cgifile, data = {id: idstr, all: true},
            function (result) {
                document.getElementById("residuals").innerHTML = result;
            }
        );
    }

    // some options for JSmol:
    var bgcolor = $(this.body).css("background-color");
    var Info;
    Info = {
        width: 320,
        height: 300,
        color: bgcolor,
        //color: "0xf0f0f0",
        shadeAtoms: false,
        addSelectionOptions: false,
        use: "HTML5",
        readyFunction: null,
        defaultModel: "",
        bondWidth: 3,
        zoomScaling: 5,
        pinchScaling: 5.0,
        mouseDragFactor: 0.9,
        touchDragFactor: 0.9,
        multipleBondSpacing: 0,
        spinRateX: -0.08,
        spinRateY: 0.05,
        spinFPS: 20,
        spin: false,
        infodiv: false,
        debug: false,
        j2sPath: "."
    };

    function advanced_search(text_in, text_out, elements_in, elements_out, cell_adv, more_res, supercell, date1, date2) {
        var cell = cell_adv.replace(/\s+/g, ' ').trim();
        if (!isValidCell(cell)) {
            cell = "";
        }
        var gridparams = {cell_search: cell, text_in: text_in, text_out: text_out, elements_in: elements_in,
                          elements_out: elements_out, more: more_res, supercell: supercell, date1:date1, date2: date2};
        //console.log(gridparams);
        var url;
        w2ui['mygrid'].request('get-records', gridparams,
            url = cgifile + "/adv_srch",
            function (result) {
                console.log(result);
            }
        );
    }

    // Search for structures of last month:
    $('#lastmsearchlink').click(function(){
        var date_now = new Date();
        var month = date_now.getUTCMonth();
        var day = date_now.getUTCDate();
        var lastmonth = new Date(date_now.getUTCFullYear(), month-1, day);
        var lastmdate = lastmonth.toISOString().split("T")[0];
        console.log(lastmdate+ ' '+ date_now.toISOString().split("T")[0]);
        //console.log(lastmdate+ ' '+ date_now.toISOString().split("T")[0]);
        // From last month to now():
        advanced_search("", "", "", "", "", "", "", lastmdate, date_now.toISOString().split("T")[0]);
    });

    // Test if a valid unit cell is in cell:
    function isValidCell(cell) {
        var scell = cell.split(" ");
        //console.log(scell);
        if (isNumericArray(scell)) {
            return !(scell.length !== 6); // return True if 6 values
        } else {
            return false;
        }
    }

    // Test if all values in array are numeric:
    function isNumericArray(array) {
        var isal = true;
        for (var i=0; i<array.length; i++) {
            if (!$.isNumeric(array[i])) {
                isal = false;
            }
        }
        return isal;
    }

    function cellsearch(cell) {
        var more_res = $('#more_results').is(':checked');
        var supercell = $('#supercells').is(':checked');
        cell = cell.replace(/\s+/g, ' ').trim();  // replace multiple spaces with one
        var params;
        var url;
        if (isValidCell(cell)) {
            w2ui['mygrid'].request('get-records',
                params = {cell_search: cell, more: more_res, supercell: supercell},
                url = cgifile + "/cellsrch",
                function (result) {
                    //console.log(result);
                    //console.log(more_res);
                }
            );
        }
    }

    function txtsearch(text) {
        var advanced = false;
        var params;
        var url;
        console.log(text);
        w2ui['mygrid'].request('get-records',
            params = {text_search: text},
            url = cgifile + "/txtsrch",
            function (result) {
                console.log(result);
            }
        );
    }

});

</script>



</html>