import React, { PropTypes } from 'react';
import { OverlayTrigger, Tooltip } from 'react_bootstrap';

/*
 * A react-bootstrap tooltip with less boilerplate
 */
var SimpleTooltip = React.createClass({

  propTypes: {
    // the text for the tooltip
    label: PropTypes.string,
    // left, right, top, bottom
    placement: PropTypes.string,
  },

  getDefaultProps() {
    return {
      placement: 'bottom'
    };
  },

  render: function() {
    var tooltip = <Tooltip>
      {this.props.label}
    </Tooltip>;

    return <OverlayTrigger
      placement={this.props.placement}
      overlay={tooltip}>
      {this.props.children}
    </OverlayTrigger>;
  },
});

export default SimpleTooltip;
