import React, { Component, Fragment } from "react";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { getIris } from "../../actions/iris";
import axios from 'axios'
import C3Chart from 'react-c3js';
import 'c3/c3.css';

var async = require("async");


export class Iris extends Component {
  static propTypes = {
    irisDataFromDB: PropTypes.array.isRequired,
    getIris: PropTypes.func.isRequired,
    updateStatus: PropTypes.func.isRequired,
    updateProgressStatus: PropTypes.func.isRequired,
    stop_feeding: PropTypes.bool.isRequired
  };

  constructor(props) {
    super(props);

    this.triggerOnlineTrain = this.triggerOnlineTrain.bind(this);

    this.state = {
      allIrisData: [],
      oneTrainingIris: undefined,
      trainedIrisData: [],
      clusteredIris: []
    }
  };

  componentWillReceiveProps(newProps) {
    console.log('Component WILL RECEIVE PROPS!')
    console.log(newProps)

    console.log(this.state)
    console.log(this.props)
    let irisDataFromDB = newProps.irisDataFromDB;
    console.log(irisDataFromDB)

    this.setState({allIrisData: irisDataFromDB})  

    console.log(this.state)
  }

  componentWillUpdate(nextProps, nextState) {
    console.log('Component WILL UPDATE!');
    console.log(nextProps)
    console.log(nextState)

    console.log(this.props)
    // old props
    let irisDataFromDB = this.props.irisDataFromDB;
    console.log(irisDataFromDB)
  }

  componentWillMount() {
    console.log('Component WILL MOUNT!');
    // this.props.setHook(this.triggerOnlineTrain)

    // this.props.getIris()
  };

  componentDidMount() {
      this.props.setHook(this.triggerOnlineTrain)

      this.props.getIris()
  };

  getAllPredictedData(callback) {
    axios.get("/api/predict").then((resp) => {
      let respData = JSON.parse(resp.data);
      let irisData = respData['result'];
      this.setState({clusteredIris: irisData})

      setTimeout(()=>{
        callback(null, null)
      }, 2000)
    })
  }

  triggerOnlineTrain() {
    let allIrisData = this.state.allIrisData;
    console.log("all", allIrisData)

    this.props.updateStatus("doing")

    this.setState({clusteredIris:[]})

    let allCount = allIrisData.length;
    async.mapSeries(allIrisData, function(oneIris, callback){
      if (this.props.stop_feeding){
        callback(null, null)
        return
      }

      let oneTrainingIris = oneIris;
      console.log("current training iris =", oneTrainingIris)

      this.setState({oneTrainingIris: oneTrainingIris});

      let {sepal_len, sepal_width, petal_len, petal_width} = oneTrainingIris;
      let postData = {
        sepal_len,
        sepal_width,
        petal_len,
        petal_width
      }
  
      axios.post("/api/feed", postData).then((resp)=>{
        console.log("data=", resp.data);
          setTimeout(() => {
            oneTrainingIris.trained = true;

            let steps = Math.ceil(95/allCount)
            this.props.updateProgressStatus(steps)

            // update view because of changed trained attr
            this.setState({allIrisData: allIrisData});

            this.getAllPredictedData(callback)
          }, 2000);
      })
    }.bind(this), function(err, results) {
      // results is now an array of stats for each file
      console.log("feeding data over!")
      this.props.updateStatus("done")
    }.bind(this));
  };

  getSepalScatterData(cluster_number){
    console.log("cluster_number=", cluster_number);

    let clusteredIris = this.state.clusteredIris;

    let data = {
      columns: [
        // ["setosa1", 0.2, 0.2],
        // ["setosa_x", 3.5, 3.0],
      ],
      xs: {
        // setosa1: 'setosa_x',
      },
      names: {

      },
      type: 'scatter'
    };

    for(let i=0; i<cluster_number; i++){
      let clusteredIrisFilter = clusteredIris.filter((oneIris) => {
        if (i === oneIris.cluster) {
          console.log("filter OK! oneIris.cluster=", oneIris.cluster);
          return true;
        }
      });
  
      let sepalLen = "sepalLen"+i;
      let sepalWidth = "sepalWidth"+i;
      let sepalLenSeries = clusteredIrisFilter.map((oneIris)=>{
        return oneIris.sepal_len;
      });
      let sepalWidthSeries = clusteredIrisFilter.map((oneIris)=>{
        return oneIris.sepal_width;
      });

      let sepalLenTrain = [sepalLen, ...sepalLenSeries];
      let sepalWidthTrain = [sepalWidth, ...sepalWidthSeries];

      data.columns.push(sepalLenTrain);
      data.columns.push(sepalWidthTrain);

      data.names[sepalLen] = "cluster"+i;
      data.xs[sepalLen] = sepalWidth;
    }

    console.log(data);
    return data;
  }

  getSepalScatterAxis(){
    return {
        x: {
            label: 'Sepal.Length',
            tick: {
                fit: false
            }
        },
        y: {
            label: 'Sepal.Width'
        }
    };
  }

  getPetalScatterData(cluster_number){
    console.log("cluster_number=", cluster_number);

    let clusteredIris = this.state.clusteredIris;

    let data = {
      columns: [
        // ["setosa1", 0.2, 0.2],
        // ["setosa_x", 3.5, 3.0],
      ],
      xs: {
        // setosa1: 'setosa_x',
      },
      names: {

      },
      type: 'scatter'
    };

    for(let i=0; i<cluster_number; i++){
      let clusteredIrisFilter = clusteredIris.filter((oneIris) => {
        if (i === oneIris.cluster) {
          console.log("filter OK! oneIris.cluster=", oneIris.cluster);
          return true;
        }
      });
  
      let petalLen = "petalLen"+i;
      let petalWidth = "petalWidth"+i;
      let petalLenSeries = clusteredIrisFilter.map((oneIris)=>{
        return oneIris.petal_len;
      });
      let petalWidthSeries = clusteredIrisFilter.map((oneIris)=>{
        return oneIris.petal_width;
      });

      let petalLenTrain = [petalLen, ...petalLenSeries];
      let petalWidthTrain = [petalWidth, ...petalWidthSeries];

      data.columns.push(petalLenTrain);
      data.columns.push(petalWidthTrain);

      data.names[petalLen] = "cluster"+i;
      data.xs[petalLen] = petalWidth;
    }

    console.log(data);
    return data;
  }

  getPetalScatterAxis(){
    return {
        x: {
            label: 'Petal.Length',
            tick: {
                fit: false
            }
        },
        y: {
            label: 'Petal.Width'
        }
    };
  }

  render() {
    let oneTrainingIris = this.state.oneTrainingIris;
    let allTrainingIrisData = [];
    if( oneTrainingIris ) {
      allTrainingIrisData.push(oneTrainingIris);
    }
    
    let cluster_number = this.props.clusterNumber;
    let sepalData = this.getSepalScatterData(cluster_number);
    let sepalAxis = this.getSepalScatterAxis();

    let petalData = this.getPetalScatterData(cluster_number);
    let petalAxis = this.getPetalScatterAxis();

    return (
      <Fragment>
        <h2>Iris Sepal Scatter Training</h2>
        <C3Chart data={sepalData} axis={sepalAxis} />

        <h2>Iris Petal Scatter Training</h2>
        <C3Chart data={petalData} axis={petalAxis} />

        <h2>Iris Data being Learned(One by One)</h2>
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

        <hr></hr>
        <h2>Iris Data to Be Learned</h2>
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
