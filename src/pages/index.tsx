import clsx from 'clsx';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';
import {createTheme, Stack, ThemeProvider, Button, Box} from "@mui/material";
import {ArrowForward} from "@mui/icons-material";


const theme = createTheme({
    components: {
        MuiButton: {
            styleOverrides: {root: {lineHeight: 0}}
        },
    },
});


function HomepageHeader() {
    const {siteConfig} = useDocusaurusContext();
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
    const {siteConfig} = useDocusaurusContext();
    return (
        <ThemeProvider theme={theme}>
            <Layout
                title={siteConfig.title}>
                <HomepageHeader/>
                <Stack spacing={5}
                       sx={{ sm: {padding: '0.5em'}, md: {padding: '2em'}}}
                       justifyContent="center"
                       alignItems="center"
                       direction={{ xs: 'column', md: 'row' }}>

                    <Box sx={{ maxWidth: '40%' , fontSize: '1.5em', py: 5}}>
                        Sito contenente la documentazione per il corso di Ingegneria del
                        Software, A.A. 2023/2024 presso l'Università degli Studi di Padova.
                    </Box>

                    <Button variant="outlined" href={'/docs/intro'}
                            sx={{backgroundColor: 'var(--ifm-color-primary)', color: '#000'}}>
                        <span>Introduzione</span>
                        <ArrowForward/>
                    </Button>
                </Stack>
            </Layout>
        </ThemeProvider>
    );
}
