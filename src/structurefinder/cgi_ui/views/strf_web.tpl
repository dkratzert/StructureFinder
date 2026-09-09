% rebase('cgi_ui/views/strf_base.tpl', title='StructureFinder')

<!-- "dropZone" adds drag&drop support for the web site -->
<div class="container" id="dropZone">
    <h2>StructureFinder</h2>


    <a type="button" class="btn btn-primary btn-sm" data-bs-toggle="collapse" data-bs-target="#adv-search"
       id="toggle_advsearch-button">Advanced Search</a>
    <a type="button" class="btn btn-warning btn-sm" id="all_structures">Show All</a>
    <a type="button" class="btn btn-outline-secondary btn-sm {{!'' if host == '127.0.0.1' else 'invisible'}}"
       id="cellsearchcsd_button"
       href="http://{{my_ip}}/csd" target="_blank">CellCheckCSD</a>

    
    % include('cgi_ui/views/simpl_search.tpl')
    
    
    % include('cgi_ui/views/advanced_search.tpl')
       

    
    <div class="row">
        <div class="column col-sm-12">
            <div id="mygrid" style="height: 450px"></div>
        </div>
    </div>

    <div class="row">
        <div class="column col-sm-12">
            <div class="card mb-3">
                <div class="card-body">
                    <span class="invisible btn-group" id="cellrow"> </span>
                    <span class="btn btn-outline-secondary bi bi-clipboard invisible" id="cell_copy_btn"
                          data-bs-toggle="tooltip" title="Copy cell to clipboard." data-clipboard-target="#hidden-cell">
                </span>
                    <span class="btn-group invisible" id="growCheckBoxgroup">
                        &nbsp;&nbsp;&nbsp;&nbsp;
                        <input type="checkbox" title="Grow Structure" value="true" id="growCheckBox" checked>Grow Structure
                </span>
                </div>
            </div>
        </div>
    </div>

    <div id="all_residuals">

        <div class="row">
            <div class="column col-md-4">
                <div class="card invisible h-100" id="moleculecolumn"
                     data-bs-toggle="tooltip" title="Completed Molecule"></div>
            </div>
            <div class="column col-md-4" id="residualstable1"></div>
            <div class="column col-md-4" id="residualstable2"></div>
        </div>


        <div class="row">
            <div class="col-sm-12">
                <span id="residuals"></span>
            </div>
        </div>
    </div>
    <address>
        <strong>
            <a href="https://dkratzert.de/structurefinder.html">StructureFinder</a>
            <span id="version"></span> by Daniel Kratzert
        </strong><br>
        <a href="mailto:dkratzert@gmx.de">dkratzert@gmx.de</a><br>
        {{!download_link}}
    </address>

</div>  <!-- End of the main container div -->


