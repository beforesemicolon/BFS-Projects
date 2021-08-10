export class BlogPost extends HTMLElement {
  title = '';
  description = '';
  link = '';
  thumbnail = '';
  
  constructor() {
    super();
    
    this.attachShadow({mode: 'open'});
  }
  
  static get observedAttributes() {
    return ['title', 'description', 'link', 'thumbnail'];
  }
  
  connectedCallback() {
    this.render();
  }
  
  attributeChangedCallback(name, oldValue, newValue) {
    // make sure it is mounted first
    if (this.isConnected) {
      switch (name) {
        case 'title':
          this.title = newValue || 'NO TITLE';
          break;
        case 'description':
          this.description = newValue || '';
          break;
        case 'link':
          this.link = newValue || '/';
          break;
        case 'thumbnail':
          this.thumbnail = newValue || '';
          break;
      }
  
      this.render()
    }
  }
  
  get style() {
    return `
        <style>
            :host {
                display: block;
            }
            
            :host * {
                box-sizing: border-box;
            }
            
            .blog-post {
                max-width: var(--blog-post-width, 300px);
                height: var(--blog-post-height, auto);
                padding: 10px 10px 25px;
                background: #f6f6f6;
                border-radius: 5px;
                position: relative;
                overflow: hidden;
            }
            
            .blog-post .thumbnail {
                background: var(--blog-post-thumb-bg, #ddd);
                width: calc(100% + 20px);
                height: 150px;
                margin-bottom: 10px;
                margin-top: -10px;
                margin-left: -10px;
                overflow: hidden;
                position: relative;
            }
            
            .blog-post .thumbnail img:not([src=""]) {
                object-fit: cover;
                position: absolute;
                left: 50%;
                top: 50%;
                transform: translate(-50%, -50%);
            }
            
            .blog-post .thumbnail img[src=""] {
                display: none;
            }
            
            .blog-post h2 {
                margin: 0;
                padding: 0 10px;
                font-family: sans-serif;
                font-size: 1.2rem;
                line-height: 135%;
            }
            
            .blog-post p {
                font-size: 0.8rem;
                line-height: 150%;
                color: #444;
                padding: 0 10px;
            }
            
            .blog-post .link:any-link {
                font-size: 0.9rem;
                text-decoration: none;
                font-weight: 900;
                letter-spacing: 0.05rem;
                color: #0a66a8;
                text-transform: capitalize;
                border-bottom: 1px solid #222;
                margin-left: 10px;
            }
        </style>
      `
  }
  
  get template() {
    return `
        <div class="blog-post">
           <div class="thumbnail">
                ${this.thumbnail ? `<img src="${this.thumbnail}" alt="${this.title}">` : ''}
            </div>
           <h2>${this.title}</h2>
           <p>${this.description}</p>
           <slot name="link"><a href="${this.link}" class="link">learn more</a></slot>
        </div>
      `
  }
  
  render() {
    this.shadowRoot.innerHTML = `${this.style}${this.template}`;
  }
}

customElements.define('blog-post', BlogPost);
