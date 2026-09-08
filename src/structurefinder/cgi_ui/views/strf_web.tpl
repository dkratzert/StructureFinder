% rebase('cgi_ui/views/strf_base.tpl', title='StructureFinder')

<!-- "dropZone" adds drag&drop support for the web site -->
<div class="container-fluid" id="dropZone">
    <h2 class="mt-4 mb-3">StructureFinder</h2>

    <div class="btn-group btn-group-sm mb-3" role="group">
        <button type="button" class="btn btn-primary" data-bs-toggle="collapse" data-bs-target="#adv-search"
           id="toggle_advsearch-button">Advanced Search</button>
        <button type="button" class="btn btn-warning" id="all_structures">Show All</button>
        <a type="button" class="btn btn-secondary {{!'' if host == '127.0.0.1' else 'd-none'}}"
           id="cellsearchcsd_button"
           href="http://{{my_ip}}/csd" target="_blank">CellCheckCSD</a>
    </div>

    
    % include('cgi_ui/views/simpl_search.tpl')
    
    
    % include('cgi_ui/views/advanced_search.tpl')
       

    
    <div class="row">
        <div class="col-12">
            <div id="mygrid" style="height: 450px;"></div>
        </div>
    </div>

    <div class="row mt-3">
        <div class="col-12">
            <div class="card">
                <div class="card-body">
                    <span class="d-none btn-group" id="cellrow"> </span>
                    <button class="btn btn-secondary d-none" id="cell_copy_btn"
                           data-bs-toggle="tooltip" title="Copy cell to clipboard." data-clipboard-target="#hidden-cell">
                        <i class="bi bi-clipboard"></i>
                    </button>
                    <span class="btn-group d-none" id="growCheckBoxgroup">
                        &nbsp;&nbsp;&nbsp;&nbsp;
                        <input type="checkbox" title="Grow Structure" value="true" id="growCheckBox" checked>Grow Structure
                    </span>
                </div>
            </div>
        </div>
    </div>

    <div id="all_residuals">

        <div class="row mt-3">
            <div class="col-md-4 card d-none" id="moleculecolumn"
                 data-bs-toggle="tooltip" title="Completed Molecule"></div>
            <div class="col-md-4" id="residualstable1"></div>
            <div class="col-md-4" id="residualstable2"></div>
        </div>


        <div class="row mt-3">
            <div class="col-12">
                <span id="residuals"></span>
            </div>
        </div>
    </div>
    <footer class="mt-5 mb-3">
        <p>
            <strong>
                <a href="https://dkratzert.de/structurefinder.html">StructureFinder</a>
                <span id="version"></span> by Daniel Kratzert
            </strong><br>
            <a href="mailto:dkratzert@gmx.de">dkratzert@gmx.de</a><br>
            {{!download_link}}
        </p>
    </footer>

</div>  <!-- End of the main container div -->

