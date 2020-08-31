import React, { Component, Fragment } from "react";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { getIris } from "../../actions/iris";

export class Iris extends Component {
  static propTypes = {
    iris: PropTypes.array.isRequired,
    getIris: PropTypes.func.isRequired
  };

  componentDidMount() {
    this.props.getIris();
  };

  render() {
    return (
      <Fragment>
        <h2>Iris To Be learned one by one</h2>
        <table className="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>sepal_len</th>
              <th>sepal_width</th>
              <th>petal_len</th>
              <th>petal_width</th>
              <th>category</th>
            </tr>
          </thead>
          <tbody>
            {this.props.iris.map(oneIris => (
              <tr key={oneIris.id}>
                <td>{oneIris.id}</td>
                <td>{oneIris.sepal_len}</td>
                <td>{oneIris.sepal_width}</td>
                <td>{oneIris.petal_len}</td>
                <td>{oneIris.petal_width}</td>
                <td>{oneIris.category}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Fragment>
    );
  }
}

const mapStateToProps = state => ({
  iris: state.iris.iris
});

export default connect(
  mapStateToProps,
  { getIris }
)(Iris);
