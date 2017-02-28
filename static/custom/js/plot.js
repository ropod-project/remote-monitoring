function Plot(container_name, variable_selection_container_name, variable_selection_class_name, data_route) {
    this.plot_container = $('#' + container_name);
    this.variable_selection_container = $('#' + variable_selection_container_name);
    this.variable_selection_class_name = variable_selection_class_name;
    this.data_route = data_route;
    this.data = [];
    this.data_labels = [];
    this.update_plot = false;
    this.current_variable = null;
}

Plot.prototype.display_data = function(variable, start_time, end_time, server_ip) {
    $.ajax({
        url: SCRIPT_ROOT + this.data_route,
        type: 'get',
        data: { variable: variable, start_time: start_time, end_time: end_time, server_ip: server_ip },
        contentType: 'application/json',
        cache: false
    }).done(function(result) {
        this.data = result.data;
        this.data_labels = result.data_labels;

        if (!this.update_plot) {
            this.plot_container.html('');
            this.add_variable_selection_checkboxes();
        }
        this.display_selected_data();

        if (real_time_data && (variable == this.current_variable)) {
            this.update_plot = true;
            setTimeout(function() {
                var start_time_ms = (new Date()).getTime() - 7260000;
                var end_time_ms = (new Date()).getTime();
                this.display_data(variable, start_time_ms, end_time_ms, ip_address);
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
    for (var i=0; i<labels.length; i++) {
        html_string += '<div class="checkbox"><label><input class="' + this.variable_selection_class_name + '" type="checkbox" value="' + i + '" checked="true" />' + this.data_labels[i] + '</label></div>';
    }
    html_string += "</div>";
    this.variable_selection_container.html(html_string);
};

Plot.prototype.display_selected_data = function () {
    var checked = $('.' + this.variable_selection_class_name + ':checked');
    var flot_data = [];
    for (var i=0; i<checked.length; i++) {
        var id = parseInt($(checked[i]).val());
        flot_data.push({ label: this.data_labels[id], data: this.data[id] });
    }
    $.plot(this.plot_container, flot_data);
};

Plot.prototype.is_empty = function() {
    return this.plot_container.html() == '';
};

Plot.prototype.reset = function() {
    this.data = [];
    this.data_labels = [];
    this.update_plot = false;
    this.current_variable = null;
    this.plot_container.html('');
    this.variable_selection_container.html('');
};
