// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import react from '@astrojs/react';

// https://astro.build/config
export default defineConfig({
	integrations: [
		starlight({
			title: 'Conversa-Suite Docs',
			social: {
				// github: 'https://github.com/withastro/starlight',
			},
			sidebar: [
				{
					label: 'Business Requirements',
					items: [
						{ label: 'Overview', slug: 'business-requirement' },
						{ label: 'User Profile Management', slug: 'business-requirement/user-profile-management' },
						{ label: 'User Management', slug: 'business-requirement/user-management' },
					],
				},
				{
					label: 'API Specification',
					items: [
						{ label: 'Overview', slug: 'api-specification' },
						{ label: 'User API', slug: 'api-specification/user' },
						{ label: 'Chatbot API', slug: 'api-specification/chatbot' },
						{ label: 'Assistant UI API', slug: 'api-specification/assistant-ui' },
						{ label: 'Data Ingestion API', slug: 'api-specification/data-ingestion' },
						{ label: 'File API', slug: 'api-specification/file-upload' },
					],
				},
				{
					label: 'Technical Reference',
					items: [
						{ label: 'Overview', slug: 'reference' },
					],
				},
			],
			customCss: [
				// Path to your custom CSS file, relative to the project root
				'./src/styles/custom.css',
			],
		}),
		react(),
	],
});
