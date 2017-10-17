function Plot(container_name, variable_selection_container_name, variable_selection_class_name, data_route) {
    this.plot_container_name = container_name;
    this.variable_selection_container_name = variable_selection_container_name;
    this.variable_selection_class_name = variable_selection_class_name;
    this.data_route = data_route;
    this.data = [];
    this.data_labels = [];
    this.update_plot = false;
    this.current_variable = null;
}

Plot.prototype.display_data = function(variable, start_time, end_time, hospital, ropod_id) {
    var parent_obj = this;
    $.ajax({
        url: SCRIPT_ROOT + parent_obj.data_route,
        type: 'get',
        data: { variable: variable, start_time: start_time, end_time: end_time, hospital: hospital, ropod_id: ropod_id },
        contentType: 'application/json',
        cache: false
    }).done(function(result) {
        parent_obj.data = result.data;
        parent_obj.data_labels = result.data_labels;

        if (!parent_obj.update_plot) {
            $('#' + parent_obj.plot_container_name).html('');
            parent_obj.add_variable_selection_checkboxes();
        }
        parent_obj.display_selected_data();

        if (real_time_data && (variable == parent_obj.current_variable)) {
            parent_obj.update_plot = true;
            setTimeout(function() {
                var start_time_ms = (new Date()).getTime() - 7260000;
                var end_time_ms = (new Date()).getTime();
                parent_obj.display_data(variable, start_time_ms, end_time_ms, server_ip);
            }, real_time_plot_update_interval);
        }

        $('#operation_indicator').hide();
    }).fail(function(jqXHR, status, error) {
        console.log(error);
        $('#operation_indicator').hide();
    });
};

Plot.prototype.add_variable_selection_checkboxes = function() {
    var html_string = '<div class="form-group">';
    for (var i=0; i<this.data_labels.length; i++) {
        html_string += '<div class="checkbox"><label><input class="' + this.variable_selection_class_name + '" type="checkbox" value="' + i + '" checked="true" />' + this.data_labels[i] + '</label></div>';
    }
    html_string += "</div>";
    $('#' + this.variable_selection_container_name).html(html_string);
};

Plot.prototype.display_selected_data = function () {
    var checked = $('.' + this.variable_selection_class_name + ':checked');
    var flot_data = [];
    for (var i=0; i<checked.length; i++) {
        var id = parseInt($(checked[i]).val());
        flot_data.push({ label: this.data_labels[id], data: this.data[id] });
    }
    $.plot($('#' + this.plot_container_name), flot_data);
};

Plot.prototype.is_empty = function() {
    return $('#' + this.plot_container_name).html() == '';
};

Plot.prototype.reset = function() {
    this.data = [];
    this.data_labels = [];
    this.update_plot = false;
    this.current_variable = null;
    $('#' + this.plot_container_name).html('');
    $('#' + this.variable_selection_container_name).html('');
};
