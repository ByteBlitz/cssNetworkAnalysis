#![allow(unused)]

use std::arch::aarch64::int64x1_t;
use std::cmp::max;

fn main() {
use pyo3::prelude::*;

#[pyfunction]
fn sum_up(start: u128, end: u128) -> u128 {
    let mut result: u128 = 0;
    for i in start..=end {
        if i % 16 == 0 {
            result += i/16;
        }
    }
    return result;
}

#[pyfunction]
fn sum_neg(start: i128, end: i128) -> i128 {
    let s;
    let e;

    if start.abs() == end.abs() {
        return 0;
    }

    if start < 0 && end > 0 {
        if -start < end {
            s = -start;
            e = end;
        } else {
            s = start;
            e = -end;
        }
    }else{
        s = start;
        e = end;
    }

    let mut result: i128 = 0;
    for i in s..=e {
        if i % 1000 == 0 {
            result += i/1000;
        }
    }
    return result;
}

#[pyclass]
struct Post {
    // properties
    creation: u32, // 4294967296 time steps at most
    creator: u32,
    fake_bias: f64,
    ups: u32,
    downs: u32,

    // statistics
    views: u32,
    success: f64
}

#[pymethods]
impl Post {
    #[new]
    fn new(creation: u32, creator: u32, fake_bias: f64) -> Self {
        Post {
            creation,
            creator,
            fake_bias,
            ups: 1,
            downs: 0,
            views: 0,
            success: 0.0
        }
    }

    fn score(&self) -> i32{
        return (self.ups - self.downs) as i32;
    }

    fn hot(&self, timestamp: u32) -> f64 {
        let s: f64 = self.score() as f64;
        let order = s.abs().max(1.0).log10();
        let sign;
        if s == 0.0 {
            sign = 0.0;
        } else {
            sign = s.signum();
        }
        let hours = timestamp - self.creation;

        return sign * order + (hours / 12) as f64
    }
}


/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn speedup(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_up, m)?)?;
    m.add_function(wrap_pyfunction!(sum_neg, m)?)?;
    m.add_class::<Post>()?;

    Ok(())
}
}
