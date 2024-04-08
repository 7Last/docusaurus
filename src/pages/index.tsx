import clsx from 'clsx';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';
import { createTheme, ThemeProvider, Grid, Button } from "@mui/material";
import { ArrowForward, GitHub } from "@mui/icons-material";


const theme = createTheme({
    components: {
        MuiButton: {
            styleOverrides: { root: { lineHeight: 0 } }
        },
    },
});


function HomepageHeader() {
    const { siteConfig } = useDocusaurusContext();
    return (
        <header className={clsx('hero hero--primary', styles.heroBanner)}>
            <div className="container">
                <Heading as="h1" className="hero__title">
                    {siteConfig.title}
                </Heading>
            </div>
        </header>
    );
}

export default function Home(): JSX.Element {
    const { siteConfig } = useDocusaurusContext();
    return (
        <ThemeProvider theme={theme}>
            <Layout
                title={siteConfig.title}>
                <HomepageHeader />

                <Grid container spacing={5} p={5} justifyContent="center" alignItems="center"
                    direction={{ xs: 'column', md: 'row' }}>
                    <Grid item xs={6} sx={{ fontSize: '1.5em' }}>
                        Sito contenente la documentazione prodotta per il corso di Ingegneria del
                        Software, A.A. 2023/2024 presso l'Università degli Studi di Padova.
                    </Grid>
                    <Grid item xs={2}>
                        <Button variant="outlined" href={'/docs/intro'}
                            sx={{ backgroundColor: 'var(--ifm-color-primary)', color: '#000' }}>
                            <span>Introduzione</span>
                            <ArrowForward />
                        </Button>
                    </Grid>

                    <Grid container spacing={3} p={5} m={2} justifyContent={'center'} alignItems={'center'}
                        direction={{ xs: 'column', md: 'row' }}>
                        <Grid item xs={4}>
                            <Heading as={'h2'}>Proof of Concept</Heading>
                            <p>
                                Realizzazione di un prototipo di un sistema che simula dati provenienti da sensori IoT,
                                li pubblica in una coda Kafka, salva su Clickhouse DB e mostra in una dashboard Grafana.
                            </p>
                        </Grid>

                        <Grid item xs={2}>
                            <Button variant="outlined"
                                sx={{
                                    color: 'var(--ifm-color-primary)',
                                    border: '2px solid var(--ifm-color-primary)',
                                    padding: 3,
                                }}
                                href={'https://github.com/7Last/SyncCity/'}
                                startIcon={<GitHub />}
                                endIcon={<ArrowForward />}>
                                Repository
                            </Button>
                        </Grid>
                    </Grid>
                </Grid>
            </Layout>
        </ThemeProvider>
    );
}
