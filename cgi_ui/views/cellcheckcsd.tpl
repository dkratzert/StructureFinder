<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>StructureFinder</title>
    
    <link rel="stylesheet" href="http://{{my_ip}}/static/w2ui/w2ui-1.4.3.min.css">
    <link rel="stylesheet" href="http://{{my_ip}}/static/bootstrap-3.3.7/css/bootstrap.min.css">
    <link rel="stylesheet" href="http://{{my_ip}}/static/bootstrap-3.3.7/css/bootstrap-theme.min.css">
    <script src="http://{{my_ip}}/static/jquery/jquery-3.2.1.min.js"></script>
    <script src="http://{{my_ip}}/static/bootstrap-3.3.7/js/bootstrap.min.js"></script>
    <script src="http://{{my_ip}}/static/w2ui/w2ui-1.4.3.min.js"></script>
    <script src="http://{{my_ip}}/static/clipboard/clipboard.min.js"></script>
    <script src="http://{{my_ip}}/static/strf_web.js"></script>
    <script> 
        var cgifile = 'http://{{my_ip}}';
    </script>
    
    
</head>
<body>

<div class="container">
    <h2>CellCheckCSD</h2>
    <div class="row">
        <div class="column col-sm-7">
            <div class="input-group input-group-sm advsearchfields">
                <span class="input-group-addon">Unit Cell</span>
                <input type="text" class="form-control form-sm" style="font-style: italic" placeholder="a b c &alpha; &beta; &gamma;" 
                       id="cell_csd_inp">
                <span class="input-group-addon input-group-btn btn-success" id="csd_search_btn">Search</span>
            </div>
        </div>
        <div class="column col-sm-2">
            <select id="centering_drop" class="btn btn-default dropdown-toggle dropdown" data-toggle="dropdown">
                <option value="1">Primitive (P)</option>
                <option value="2">A-centered (A)</option>
                <option value="3">B-centered (B)</option>
                <option value="4">C-centered (C)</option>
                <option value="5">Face-centered (F)</option>
                <option value="6">Body-centered (I)</option>
                <option value="7">Rhombohedral (R)</option>
            </select>
        </div>
        <div class="column col-sm-2">
            <a type="button" class="btn btn-default btn-sm" id="backtomain_button" href="http://{{my_ip}}">Back to StructureFinder</a>
        </div>
    </div>
    <div class="row">
        <div class="column col-sm-12">
            <div id="my_ccdc_grid" style="height: 450px">
                
            </div>
        </div>
    </div>    


    <div class="row">
    <div class="col-sm-12">
        <address>
            <strong><a href="https://www.xs3.uni-freiburg.de/research/structurefinder">StructureFinder</a> 
                <span id="version"></span> by Daniel Kratzert</strong><br>
          <a href="mailto:daniel.kratzert@ac.uni-freiburg.de">daniel.kratzert@ac.uni-freiburg.de</a>
        </address>
    </div>
</div>
    

</div>  <!-- End of main container -->



<script>
$(document).ready(function($){
    
    my_ccdc_grid = $('#my_ccdc_grid');
    
    // The main structures table:
    my_ccdc_grid.w2grid({
        name: 'my_ccdc_grid',
        header: 'StructureFinder',
        url: cgifile+"/csd",
        method: 'GET',
        show: {
            toolbar: false,
            footer: true
        },
        columns: [
            {field: 'chemical_formula',  caption: 'formula', size: '20%', sortable: false, attr: 'align=left'},
            {field: 'cell_length_a',     caption: '<i>a</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_length_b',     caption: '<i>b</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_length_c',     caption: '<i>c</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_angle_alpha',  caption: '<i>&alpha;</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_angle_beta',   caption: '<i>&beta;</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_angle_gamma',  caption: '<i>&gamma;</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'recid',             caption: 'Itentity', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_length_c',     caption: 'Space Grp.', size: '10%',  sortable: false, resizable: true}
        ],
        searches: [
            {field: 'filename', caption: 'filename', type: 'text'},
            {field: 'dataname', caption: 'dataname', type: 'text'},
            {field: 'path', caption: 'directory', type: 'text'}
        ],
        //sortData: [{field: 'dataname', direction: 'ASC'}],
        onDblClick:function(event) {
            strid = event.recid;
            showprop(strid);
            console.log(event);
        }
    });
    
    //gets the window's height
    var b = $(window).height();
    var h = b * 0.50;
    if (h < 200) {
        h = 220;
    }
    // Define the grid height to 35% of the screen:
    my_ccdc_grid.css("height", h);
    
    
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
    
    
    // Cell search Button clicked:
    $("#csd_search_btn").click(function(event) {
        var cell = document.getElementById("cell_csd_inp").value;
        console.log(cell);
        csdcellsearch(cell);
    });
    
    function csdcellsearch(cell) {
        var more_res = $('#more_results').is(':checked');
        var centering = $('#centering_drop').valueOf();
        cell = cell.replace(/\s+/g, ' ').trim();  // replace multiple spaces with one
        cell = cell.replace(/,/g, '.');  // replace comma with point
        //console.log(cell);
        var params;
        var url;
        if (isValidCell(cell)) {
            w2ui['my_ccdc_grid'].request('get-records',
                params = {cell: cell, centering: centering},
                url = cgifile + "/csd",
                function (result) {
                    //displayresultnum(result);
                    console.log(result);
                    //console.log(more_res);
                }
            );
        }
    }
});

</script>

</body>
</html>