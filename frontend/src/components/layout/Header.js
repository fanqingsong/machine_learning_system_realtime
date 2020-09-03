import React, { Component, Fragment } from "react";
import { Link, Redirect } from "react-router-dom";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { logout } from "../../actions/auth";

import { Nav } from 'react-bootstrap';

export class Header extends Component {
  static propTypes = {
    auth: PropTypes.object.isRequired,
    logout: PropTypes.func.isRequired
  };

  constructor(props) {
    super(props);

    this.state = {
      activeKey: "data",
    }
  };

  componentDidMount(){
    let activeKey = location.hash.slice(2);
    activeKey = activeKey == "" ? "data" : activeKey;

    this.setState({activeKey: activeKey});
  };

  handleSelect(selectedKey) {
    this.setState({activeKey: selectedKey});
  };

  render() {
    const { isAuthenticated, user } = this.props.auth;

    const authLinks = (
      <ul className="navbar-nav ml-auto mt-2 mt-lg-0">
        <span className="navbar-text mr-3">
          <strong>{user ? `Welcome ${user.username}` : ""}</strong>
        </span>
        <li className="nav-item">
          <button
            onClick={this.props.logout}
            className="nav-link btn btn-info btn-sm text-light"
          >
            Logout
          </button>
        </li>
      </ul>
    );

    const guestLinks = (
      <ul className="navbar-nav ml-auto mt-2 mt-lg-0">
        <li className="nav-item">
          <Link to="/register" className="nav-link">
            Register
          </Link>
        </li>
        <li className="nav-item">
          <Link to="/login" className="nav-link">
            Login
          </Link>
        </li>
      </ul>
    );


    let activeKey = this.state.activeKey;
    const menus = (
      <Nav variant="pills" activeKey={activeKey} defaultActiveKey="data"  onSelect={this.handleSelect.bind(this)}>
        <Nav.Item>
          <Nav.Link eventKey="data" title="Data" href="#/data">
            Data(iris)
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link eventKey="explore" title="Explore" href="#/explore">
            Explore
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link eventKey="train" title="Train" href="#/train">
            Train(Online)
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link eventKey="predict" title="Predict" href="#/predict">
            Predict
          </Nav.Link>
        </Nav.Item>
      </Nav>
    );

    return (
      <Fragment>
        <div className="container">
          <nav className="navbar navbar-expand-sm navbar-light bg-light">
            <div className="collapse navbar-collapse" id="navbarTogglerDemo01">
              <a className="navbar-brand" href="#">
                Machine Learning System
              </a>
            </div>
            {isAuthenticated ? authLinks : guestLinks}
          </nav>

          { isAuthenticated ? menus : <div></div> }
        </div>
      </Fragment>
    );
  }
}

const mapStateToProps = state => ({
  auth: state.auth
});

export default connect(
  mapStateToProps,
  { logout }
)(Header);
