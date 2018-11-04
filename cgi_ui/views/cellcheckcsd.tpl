
% rebase('cgi_ui/views/strf_base.tpl', title='CellCheckCSD')

<script src="http://{{my_ip}}/static/strf_web_csd.js"></script>

<div class="container"  id="dropZone">
    <h2>CellCheckCSD</h2>
    <div class="row">
        <div class="column col-sm-7">
            <div class="input-group input-group-sm advsearchfields">
                <span class="input-group-addon">Unit Cell</span>
                <input type="text" class="form-control form-sm" style="font-style: italic" placeholder="a b c &alpha; &beta; &gamma;" 
                       id="cell_csd_inp" value="{{str_id}}">
                <span class="input-group-addon input-group-btn btn-success" id="csd_search_btn">Search</span>
            </div>
        </div>
        <div class="column col-sm-2">
            <select id="centering_drop" class="dropdown dropdown-toggle btn-md" data-toggle="dropdown">
                <option value="{{cent}}" {{!'selected="selected"' if cent == 0 else ""}}>Primitive (P)</option>
                <option value="{{cent}}" {{!'selected="selected"' if cent == 1 else ""}}>A-centered (A)</option>
                <option value="{{cent}}" {{!'selected="selected"' if cent == 2 else ""}}>B-centered (B)</option>
                <option value="{{cent}}" {{!'selected="selected"' if cent == 3 else ""}}>C-centered (C)</option>
                <option value="{{cent}}" {{!'selected="selected"' if cent == 4 else ""}}>Face-centered (F)</option>
                <option value="{{cent}}" {{!'selected="selected"' if cent == 5 else ""}}>Body-centered (I)</option>
                <option value="{{cent}}" {{!'selected="selected"' if cent == 6 else ""}}>Rhombohedral (R)</option>
            </select>
        </div>
        <div class="column col-sm-2">
            <a type="button" class="btn btn-default btn-sm" id="backtomain_button" href="http://{{my_ip}}">Back to StructureFinder</a>
        </div>
    </div>

    <!-- ------------- The main table: ------------ -->
    <div class="row">
        <div class="column col-sm-12">
            <div class="w2ui-grid" id="my_ccdc_grid" style="height: 450px">
                
            </div>
        </div>
    </div>    

<div class="row">
    <div class="column col-sm-12">
        <div class="panel panel-default">
            <div class="panel-body">
                <span id="found_csd"> </span>
            </div>
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

