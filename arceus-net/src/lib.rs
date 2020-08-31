// #[macro_use]
extern crate pyo3;

use futures::future;
// use native_tls;
use pyo3::prelude::*;
use std::net::SocketAddr;
use tokio::net::TcpStream;
use tokio::prelude::*;
use tokio::runtime::Runtime;
use tokio::time::Duration;

#[pyclass]
struct ConnectionManager {
    address: SocketAddr,
    streams: Vec<TcpStream>,
}

#[pymethods]
impl ConnectionManager {
    #[new]
    fn new(host: String, _ssl: bool) -> Self {
        ConnectionManager {
            address: host.parse::<SocketAddr>().unwrap(),
            streams: Vec::new(),
        }
    }

    fn connect(&mut self, connections: u32) -> PyResult<()> {
        let mut rt = Runtime::new().unwrap();

        async fn create_stream(address: SocketAddr) -> Option<TcpStream> {
            let r = TcpStream::connect(address).await;
            match r.ok() {
                Some(stream) => {
                    stream.set_keepalive(Some(Duration::from_millis(1000))).unwrap_or(());
                    Some(stream)
                },
                None => None
            }
        }

        rt.block_on(async {
            self.streams.extend(
                future::join_all((0..connections).map(|_| create_stream(self.address)))
                    .await
                    .into_iter()
                    .filter_map(|s| s)
            );
        });

        Ok(())
    }

    fn send(&mut self, payload: &[u8]) -> PyResult<()> {
        let mut rt = Runtime::new().unwrap();

        rt.block_on(future::join_all(
            self.streams.iter_mut().map(|s| s.write_all(payload)),
        ));
        
        Ok(())
    }
}

/// Arceus networking library. Implemented in Rust.
#[pymodule]
fn arceus_net(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<ConnectionManager>()?;
    Ok(())
}
