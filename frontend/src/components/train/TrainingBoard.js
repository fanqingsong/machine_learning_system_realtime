import React, { Component, Fragment } from "react";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { getIris } from "../../actions/iris";
var async = require("async");

export class Iris extends Component {
  static propTypes = {
    irisDataFromDB: PropTypes.array.isRequired,
    getIris: PropTypes.func.isRequired
  };

  constructor(props) {
    super(props);

    this.state = {
      allIrisData: [],
      oneTrainingIris: undefined,
      trainedIrisData: []
    }
  };

  componentDidMount() {
    this.props.getIris();
    let allIrisData = this.props.irisDataFromDB;

    this.setState({allIrisData: allIrisData})

    setTimeout(()=>{
      this.triggerOnlineTrain()
    }, 1000)
  };

  triggerOnlineTrain() {
    let allIrisData = this.state.allIrisData;
    console.log("all", allIrisData)
    async.mapSeries(allIrisData, function(oneIris, callback){
      let oneTrainingIris = oneIris;
      console.log("current training iris =", oneTrainingIris)

      setTimeout(() => {
        oneTrainingIris.trained = true;
        this.setState({oneTrainingIris: oneTrainingIris});

        // update view because of changed trained attr
        this.setState({allIrisData: allIrisData});

        callback(null, null)
      }, 1000);
    }.bind(this), function(err, results) {
      // results is now an array of stats for each file
    });
  };

  render() {
    let oneTrainingIris = this.state.oneTrainingIris;
    let allTrainingIrisData = [];
    if( oneTrainingIris ) {
      allTrainingIrisData.push(oneTrainingIris);
    }
    
    return (
      <Fragment>
        <h2>Iris Data being learned</h2>
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
            {allTrainingIrisData.map(oneIris => (
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

        <h2>Iris Data to be learned one by one</h2>
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
            {this.state.allIrisData.filter(oneIris=>oneIris.trained!=true).map(oneIris => (
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
  irisDataFromDB: state.iris.iris
});

export default connect(
  mapStateToProps,
  { getIris }
)(Iris);
