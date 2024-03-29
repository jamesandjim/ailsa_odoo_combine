odoo.define('web_grid.MockServer', function (require) {
"use strict";

var MockServer = require('web.MockServer');

MockServer.include({
    /**
     * @override
     */
    _performRpc: function (route, args) {
        if (args.method === 'read_grid') {
            return this._mockReadGrid(args.model, args.kwargs);
        } else if (args.method === 'read_grid_domain') {
            return this._mockReadGridDomain(args.model, args.kwargs);
        } else if (args.method === 'adjust_grid') {
            var adjust = args.kwargs.context.grid_adjust;
            var lines = this._mockSearchReadController({
                model: args.model,
                domain: adjust.row_domain,
                fields: [],
            });
            var newID = this._mockCopy(args.model, lines.records[0].id);
            var newRecord = _.findWhere(this.data[args.model].records, {id: newID});
            newRecord[adjust.cell_field] = adjust.change;
            newRecord[adjust.column_field] = adjust.column_value.split('/')[0];
            return $.when({});
        } else {
            return this._super(route, args);
        }
    },
    /**
     * @private
     * @param {string} model
     * @param {Object} kwargs
     * @returns {Deferred}
     */
    _mockReadGrid: function (model, kwargs) {
        var self = this;

        // various useful dates
        var gridAnchor = moment(kwargs.context.grid_anchor || this.currentDate);
        var today = moment();
        var span = kwargs.range.span;
        var start = gridAnchor.clone().startOf(span === 'week' ? 'isoWeek' : 'month');
        var end = gridAnchor.clone().endOf(span === 'week' ? 'isoWeek' : 'month');
        var nextAnchor = gridAnchor.clone().add(1, span === 'week' ? 'weeks' : 'month').format('YYYY-MM-DD');
        var prevAnchor = gridAnchor.clone().subtract(1, span === 'week' ? 'weeks' : 'month').format('YYYY-MM-DD');

        // compute columns
        var columns = [];
        var current = start.clone().subtract(1, 'days');

        while (!current.isSame(end, 'days')) {
            current.add(1, 'days');
            var dayStr = current.format('YYYY-MM-DD');
            var nextDayStr = current.clone().add(1, 'days').format('YYYY-MM-DD');
            columns.push({
                is_current: current.isSame(today),
                domain: ["&", ["date", ">=", dayStr], ["date", "<", nextDayStr]],
                values: {date: [dayStr + '/' + nextDayStr, current.format('ddd,\nMMM\u00a0DD')]}
            });
        }

        // compute rows
        var rows = [];
        var domain = [
            '&',
            [kwargs.col_field, '>=', start.format('YYYY-MM-DD')],
            [kwargs.col_field, '<', end.format('YYYY-MM-DD')]
        ].concat(kwargs.domain);

        var groups = this._mockReadGroup(model, {
            domain: domain,
            fields: [kwargs.cell_field],
            groupby: [kwargs.row_fields[0]],
        });
        _.each(groups, function (group) {
            var groupValue = {};
            groupValue[kwargs.row_fields[0]] = group[kwargs.row_fields[0]];
            var groupDomain = ['&'].concat(domain).concat(group.__domain);
            if (kwargs.row_fields[1]) {
                var subGroups = self._mockReadGroup(model, {
                    domain: groupDomain,
                    fields: [kwargs.cell_field],
                    groupby: [kwargs.row_fields[1]],
                });
                _.each(subGroups, function (subGroup) {
                    var subGroupDomain = ['&'].concat(groupDomain, subGroup.__domain);
                    var values = _.extend({}, groupValue);
                    values[kwargs.row_fields[1]] = subGroup[kwargs.row_fields[1]] || false;
                    rows.unshift({
                        domain: subGroupDomain,
                        values: values,
                    });
                });
            } else {
                rows.unshift({
                    domain: groupDomain,
                    values: groupValue,
                });
            }
        });

        // generate cells
        var grid = [];
        _.each(rows, function (row) {
            var cells = [];
            _.each(columns, function (col) {
                var cellDomain = ['&'].concat(row.domain).concat(col.domain);
                var records = self._mockSearchReadController({
                    model: model,
                    domain: cellDomain,
                    fields: [kwargs.cell_field],
                });
                var value = 0;
                _.each(records.records, function (rec) {
                    value += rec[kwargs.cell_field];
                });
                cells.push({
                    size: records.length,
                    value: value,
                    is_current: col.is_current,
                    domain: cellDomain,
                });

            });
            grid.push(cells);
        });

        return $.when({
            cols: columns,
            rows: rows,
            grid: grid,
            prev: {
                default_date: prevAnchor,
                grid_anchor: prevAnchor,
            },
            next: {
                default_date: nextAnchor,
                grid_anchor: nextAnchor,
            },
        });
    },
    /**
     * @TODO: this is not very generic but it works for the tests
     * @private
     * @returns {Deferred}
     */
    _mockReadGridDomain: function () {
        return $.when([
            '&',
            ['date', '>=', '2017-01-01'],
            ['date', '<=', '2017-01-31'],
        ]);
    },
});

});
